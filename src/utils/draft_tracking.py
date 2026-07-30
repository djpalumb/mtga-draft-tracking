import pandas as pd
from collections import Counter
import os
from typing import List

class DraftTracker:
    def __init__(
        self,
        expansion: str,
        pick_two: bool = False,
    ):
        # Indexed with two ints (pack, pick), starting at 0
        # Note, logfile starts at 1
        self.picks = {}
        self.seen = {}
        self.pick_two = pick_two
        self.expansion = expansion

    def __str__(self):
        lines = [
            f"DraftTracker(pick_two={self.pick_two}, expansion={self.expansion})",
            f"  Seen entries: {len(self.seen)}",
            f"  Pick entries: {len(self.picks)}",
        ]

        all_keys = sorted(set(self.seen) | set(self.picks))

        for pack, pick in all_keys:
            seen = self.seen.get((pack, pick))
            chosen = self.picks.get((pack, pick))

            lines.append(
                f"  Pack {pack}, Pick {pick}: "
                f"seen={seen}, picked={chosen}"
            )

        return "\n".join(lines)
    

    def get_current_index(self):
        keys = self.seen.keys()
        max_pack = max([x for (x,y) in keys])
        max_pick = max([y for (x,y) in keys])

        return max_pack, max_pick

    def get_pack_order(
        self
    ):
        # Create a list of key pairs to index that represents the order of the draft
        keys = self.seen.keys()
        pack_inds = [x for (x,y) in keys]
        pick_inds = [y for (x,y) in keys]
        ret_list = []
        for x in pack_inds:
            for y in pick_inds:
                ret_list.append((x,y))
        return ret_list

    def add_seen(
        self,
        pack: int,
        pick: int,
        card_id_list: List[int]
    ):
        self.seen[(pack, pick)] = card_id_list

    def add_pick(
        self,
        pack: int,
        pick: int,
        card_ids_selected: List[int]
    ):
        if self.pick_two:
            self.picks[(pack, pick)] = card_ids_selected[0:2]
        else:
            self.picks[(pack, pick)] = card_ids_selected[0]

    def get_seen(
        self,
        pack: int,
        pick: int,
    ):
        if (pack, pick) in self.seen.keys():
            ret = self.seen[(pack, pick)]
        else:
            ret = None

        return ret

    def get_pick(
        self,
        pack: int,
        pick: int,
    ):
        if (pack, pick) in self.picks.keys():
            ret = self.picks[(pack, pick)]
        else:
            ret = None

        return ret

    def get_known_missing(
        self,
        pack: int,
        pick: int
    ):
        """
        If this pack is a wheel pack, determine cards that disappeared
        since the last time this player saw the pack.
        """

        if self.pick_two:
            prev_pick = pick - 4
        else:
            prev_pick = pick - 8

        if prev_pick < 0:
            return []

        if (pack, prev_pick) not in self.seen:
            return []

        if (pack, pick) not in self.seen:
            return []

        previous_seen = Counter(self.seen[(pack, prev_pick)])
        current_seen = Counter(self.seen[(pack, pick)])

        known_missing = previous_seen - current_seen

        # Remove cards you personally took
        if (pack, prev_pick) in self.picks:
            known_missing -= Counter(self.picks[(pack, prev_pick)])

        return list(known_missing.elements())