import pandas as pd
from collections import Counter
import os
from typing import List

class DraftTracker:
    def __init__(
        self,
        pick_two: bool = False,
    ):
        # Indexed with two ints (pack, pick), starting at 0
        # Note, logfile starts at 1
        self.picks = {}
        self.seen = {}
        self.pick_two = pick_two

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
        If this pack is a wheel pack, we will know what was already in the pack and should be able to determine the list of ids that is missing from it.
        """

        if self.pick_two:
            prev_pick = pick-4
        else:
            prev_pick = pick-8

        if prev_pick < 0:
            return []

        if (pack, prev_pick) in self.seen and (pack, pick) in self.seen:
            return list((Counter(self.seen[((pack, prev_pick))]) - Counter([((pack, pick))])).elements())

        else:
            return []