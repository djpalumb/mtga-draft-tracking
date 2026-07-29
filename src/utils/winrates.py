import pandas as pd
import os
import sys
from typing import List
import re

CARD_IDS_REF_FILEPATH = os.path.join('data', 'cards.csv')

CARD_WINRATE_FILEPATH_MSH = os.path.join('data', 'card-ratings-MSH-2026-07-29.csv')

def get_cards_winrate_by_name(
    card_names: List[str],
    card_winrate_ref_filepath: str = CARD_WINRATE_FILEPATH_MSH,
    win_metric: str = 'GIH WR'
):
    card_df = pd.DataFrame({'Name': card_names})

    # Merge in metric
    winrate_df = pd.read_csv(card_winrate_ref_filepath, index_col=None)

    card_df = card_df.merge(
        winrate_df[['Name', f'{win_metric}']],
        on='Name',
        how='left'
    )

    def winrate_str_to_float(s:str):
        try:
            ret = float(s.strip().rstrip("%")) / 100
            ret = float(f'{ret:4f}')
        except:
            ret = None
        return ret

    # remove % and return as float
    card_df[f'{win_metric}'] = card_df[f'{win_metric}'].apply(lambda x:  winrate_str_to_float(x))
    card_df = card_df.sort_values(by=[f'{win_metric}'], ascending=False, ignore_index=True)

    return card_df[['Name', f'{win_metric}']]


def get_cards_winrate_by_id(
    card_ids: List[int],
    card_ids_ref_filepath: str = CARD_IDS_REF_FILEPATH,
    card_winrate_ref_filepath: str = CARD_WINRATE_FILEPATH_MSH,
    win_metric: str = 'GIH WR'
):
    # Merge to get all the names for the cards
    card_df = pd.DataFrame({'id': card_ids})
    card_names_df = pd.read_csv(card_ids_ref_filepath, index_col=None)

    card_df = card_df.merge(
        card_names_df,
        on='id',
        how='left'
    )

    output = get_cards_winrate_by_name(
        card_df['name'].tolist(),
        card_winrate_ref_filepath,
        win_metric
    )

    return output

if __name__ == '__main__':
    # test
    test_log = os.path.join('data', 'sample_draft_logs.txt')
    with open(test_log, 'r') as f:
        text = f.read()

    matches = re.findall(r'"PackCards":"(.*)"\}', text)
    first_pack = [int(x) for x in matches[0].split(',')]

    winrates_df = get_cards_winrate_by_id(first_pack)
    for i, row in winrates_df.iterrows():
        print(f'{row['Name']}: {row['GIH WR']}')