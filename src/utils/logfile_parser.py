"""
Utilities for parsing MTGA draft logs.

This module converts raw MTGA Unity logs into DraftTracker updates.

Supported events:
- EventJoin: detects draft start and expansion
- Draft.Notify: captures cards currently seen in a pack
- EventPlayerDraftMakePick: captures completed picks
- DraftCompleteDraft: detects draft completion
"""

import os
import re
from typing import List
from src.utils.draft_tracking import DraftTracker

def check_start_of_draft_line(logfile_str: str) -> str | None:
    pattern = r'\[UnityCrossThreadLogger\]==> EventJoin {.*\\"EventName\\":\\"\S*Draft'

    matches = re.findall(pattern, logfile_str, re.DOTALL | re.IGNORECASE)
    if len(matches) > 0:
        # Determine set
        set_pattern = r'\[UnityCrossThreadLogger\]==> EventJoin {.*\\"EventName\\":\\"\S*Draft_(.*)_'
        set_matches = re.findall(set_pattern, logfile_str, re.DOTALL | re.IGNORECASE)
        if len(set_matches) > 0:
            return set_matches[0]
        else:
            # Unknown set
            return ''
    else:
        return None

def find_last_draft_in_log_file(logfile_str_lines: List[str]):
    # Parse in inverse order to find the latest draft in file
    for i, row in enumerate(logfile_str_lines[::-1]):
        ret_set = check_start_of_draft_line(row)
        if ret_set is None:
            continue
        else:
            return i, ret_set

    return None, None

def check_for_seen_line(logfile_str: str) -> tuple[str, str, str] | None:
    pattern = r'\[UnityCrossThreadLogger\]Draft.Notify {.*\"SelfPick\":(\d*),\"SelfPack\":(\d),\"PackCards\":\"([\d\,]*)\"}'
    matches = re.findall(pattern, logfile_str, re.DOTALL | re.IGNORECASE)
    if len(matches) > 0:
        return matches[0]
    else:
        return None

def check_for_pick_line(logfile_str: str):
    pattern = r'\[UnityCrossThreadLogger\]==> EventPlayerDraftMakePick {.*\\"GrpIds\\":\[([\d\,]*)\],\\"Pack\\":(\d*),\\"Pick\\":(\d*)}'
    matches = re.findall(pattern, logfile_str, re.DOTALL | re.IGNORECASE)
    if len(matches) > 0:
        return matches[0]
    else:
        return None

def check_draft_complete_line(logfile_str: str):
    pattern = r'\[UnityCrossThreadLogger\]==> DraftCompleteDraft'
    matches = re.findall(pattern, logfile_str, re.DOTALL | re.IGNORECASE)
    if len(matches) > 0:
        return True
    else:
        return False
    

def process_logfile_line(draft: DraftTracker | None, line: str):
    """
    Process a single MTGA log line and update draft state.

    A new DraftTracker is created when a draft start event is found.
    Existing drafts are updated when card seen/pick events occur.

    Returns:
        Tuple containing:
            - Updated DraftTracker object
            - Whether the draft state changed
    """

    # New draft
    ret_set = check_start_of_draft_line(line)
    if ret_set is not None:
        draft = DraftTracker(
            expansion=ret_set.strip(),
            pick_two='PickTwoDraft' in line
        )
        return draft, True

    if draft is None:
        return None, False

    # Draft complete
    if check_draft_complete_line(line):
        draft.ended = True
        return draft, True

    update = False

    # Seen
    matches = check_for_seen_line(line)
    if matches:
        pick = int(matches[0])
        pack = int(matches[1])
        ids = [int(x) for x in matches[2].split(',')]
        draft.add_seen(pack, pick, ids)
        update = True

    # Pick
    matches = check_for_pick_line(line)
    if matches:
        pick = int(matches[2])
        pack = int(matches[1])
        ids = [int(x) for x in matches[0].split(',')]
        draft.add_pick(pack, pick, ids)
        update = True

    return draft, update


def parse_through_draft_logs(logfile_str_lines: List[str], max_lines: int = 1000) -> DraftTracker:
    """
    Reconstruct the current draft state from historical MTGA logs.

    Only the most recent draft in the log file is considered.

    Args:
        logfile_str_lines: MTGA log file contents.
        max_lines: Safety limit to prevent scanning indefinitely.

    Returns:
        DraftTracker representing the current or completed draft.
    """
    # Find the start of the last draft
    draft_start_reverse_ind, ret_set = find_last_draft_in_log_file(logfile_str_lines)
    if draft_start_reverse_ind is None:
        return None

    draft_start_forward_ind = len(logfile_str_lines) - draft_start_reverse_ind - 1

    # Check if picktwo draft
    if 'PickTwoDraft' in logfile_str_lines[draft_start_forward_ind]:
        pick_two = True
    else:
        pick_two = False

    # Create a draft object to keep track of logs
    draft = DraftTracker(
        expansion=ret_set, 
        pick_two=pick_two
    )

    # Parsed start of draft line already
    lines_parsed = 1

    # parse lines, looking for seen and pick lines
    for line in logfile_str_lines[draft_start_forward_ind+1:]:
        draft, _ = process_logfile_line(draft, line)
        if draft.ended:
            return draft

        lines_parsed += 1
        if lines_parsed >= max_lines:
            raise Exception(f'Could not reach end of draft before max parse lines')

    # Reached the end of logfile without end to draft, draft is ongoing, return draft object
    return draft


class DraftLogListener:
    def __init__(self, logfile_path: str, draft: DraftTracker | None):
        self.draft = draft

        self.file = open(logfile_path, "r", encoding="utf-8")

        # Start listening only for future writes
        self.file.seek(0, os.SEEK_END)

    def poll(self) -> bool:
        """
        Processes any newly-written log lines.

        Returns True if the draft changed.
        """

        changed = False

        while True:
            line = self.file.readline()

            # No more data currently available
            if not line:
                break

            self.draft, updated = process_logfile_line(self.draft, line)
            changed |= updated

        return changed

    def close(self):
        self.file.close()


if __name__ == '__main__':
    logfile_path = os.path.join('test_files', 'sample_draft_logs.log')    
    with open(logfile_path, 'r', encoding='utf-8') as f:
        logfile_str_lines = f.readlines()

    ret = parse_through_draft_logs(logfile_str_lines)
    print(f'Output:\n{ret}')