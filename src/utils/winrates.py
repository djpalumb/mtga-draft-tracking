import pandas as pd
import os
import sys
from typing import List
import re

CARD_IDS_REF_FILEPATH = os.path.join('data', 'cards.csv')

CARD_WINRATE_FILEPATH_MSH = os.path.join('data', 'card-ratings-MSH-2026-07-29.csv')


def get_winrate_grade_cutoffs(
    filepath,
    min_games=2500,
    win_metric="GIH WR",
    games_col="# GP"
):
    """
    Returns winrate thresholds corresponding to percentile grades.

    Returns:
        dict:
            grade -> minimum winrate required
    """

    df = pd.read_csv(filepath)

    df = df.rename(columns={"Name": "name"})

    def parse_wr(x):
        try:
            return float(str(x).replace("%", "")) / 100
        except:
            return None

    df[win_metric] = df[win_metric].apply(parse_wr)

    # Filter unreliable cards
    df = df[df[games_col] >= min_games]

    winrates = df[win_metric].dropna()

    # Higher percentile = better card
    cutoffs = {
        "S": winrates.quantile(0.95),
        "A": winrates.quantile(0.85),
        "B": winrates.quantile(0.65),
        "C": winrates.quantile(0.30),
        "D": winrates.quantile(0.15)
    }

    return cutoffs


def get_cards_winrate_by_name(
    card_names: List[str],
    card_winrate_ref_filepath: str = CARD_WINRATE_FILEPATH_MSH,
    win_metric: str = 'GIH WR'
):
    """
    Function pulls winrates of cards given their names and the corresponding set winrate file.

    Args:
        card_names - List[str]            
            List of card names
        card_winrate_ref_filepath - str    
            Path to winrate file from 17 lands
        win_metric - str    
            Col name used for winrrate
    
    Return 
        Dataframe with name and winrate columns
    """

    card_df = pd.DataFrame({'name': card_names})

    # Merge in metric
    winrate_df = pd.read_csv(card_winrate_ref_filepath, index_col=None)
    winrate_df = winrate_df.rename(columns={'Name': 'name'})

    card_df = card_df.merge(
        winrate_df[['name', f'{win_metric}']],
        on='name',
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

    return card_df[['name', f'{win_metric}']]


def get_cards_winrate_by_id(
    card_ids: List[int],
    card_ids_ref_filepath: str = CARD_IDS_REF_FILEPATH,
    card_winrate_ref_filepath: str = CARD_WINRATE_FILEPATH_MSH,
    win_metric: str = 'GIH WR'
):

    """
    Function pulls winrates of cards given their card ids and the corresponding set winrate file.

    Args:
        card_ids - List[int]            
            List of card ids
        card_ids_ref_filepath - str
            Path to id refernce file from 17 lands
        card_winrate_ref_filepath - str    
            Path to winrate file from 17 lands
        win_metric - str    
            Col name used for winrrate
    
    Return 
        Dataframe with name and winrate columns, as well as other columns from card id ref file
    """

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

    ret = output.merge(
        card_df,
        on='name',
        how='left'
    )

    return ret

if __name__ == '__main__':
    # test
    test_log = os.path.join('test_files', 'sample_draft_logs.txt')
    with open(test_log, 'r') as f:
        text = f.read()

    matches = re.findall(r'"PackCards":"(.*)"\}', text)
    first_pack = [int(x) for x in matches[0].split(',')]

    winrates_df = get_cards_winrate_by_id(first_pack)
    for i, row in winrates_df.iterrows():
        print(f'{row['name']}: {row['GIH WR']}')
