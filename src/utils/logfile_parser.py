import os
import pandas
import re
from typing import List
from src.utils.draft_tracking import DraftTracker

def check_start_of_draft_line(logfile_str: str):
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

def check_for_seen_line(logfile_str: str):
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

def find_last_draft_in_log_file(logfile_str_lines: List[str]):
    for i, row in enumerate(logfile_str_lines[::-1]):
        ret_set = check_start_of_draft_line(row)
        if ret_set is None:
            continue
        else:
            return i, ret_set

    return None, None

def parse_through_draft_logs(logfile_str_lines: List[str], max_lines: int = 200) -> DraftTracker:
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

    lines_parsed = 1

    # parse lines, looking for seen and pick lines
    for line in logfile_str_lines[draft_start_forward_ind+1:]:
        # Check if draft complete line
        if check_draft_complete_line(line):
            return draft

        # Check if "seen" line
        matches = check_for_seen_line(line)
        if matches is not None:
            pick = int(matches[0])
            pack = int(matches[1])
            ids = [int(x) for x in matches[2].split(',')]
            draft.add_seen(pack, pick, ids)

        # Check if "pick" line
        matches = check_for_pick_line(line)
        if matches is not None:
            pick = int(matches[2])
            pack = int(matches[1])
            ids = [int(x) for x in matches[0].split(',')]
            draft.add_pick(pack, pick, ids)

        lines_parsed += 1
        if lines_parsed >= max_lines:
            raise Exception(f'Could not reach end of draft before max parse lines')

    # Reached the end of logfile without end to draft, draft is ongoing, return draft object
    return draft


if __name__ == '__main__':
    logfile_path = os.path.join('test_files', 'sample_draft_logs.txt')    
    with open(logfile_path, 'r', encoding='utf-8') as f:
        logfile_str_lines = f.readlines()

    ret = parse_through_draft_logs(logfile_str_lines)
    print(f'Output:\n{ret}')