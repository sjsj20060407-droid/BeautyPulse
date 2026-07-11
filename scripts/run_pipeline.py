from pathlib import Path
import argparse
import sys

import pandas as pd

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"src"))
from beautypulse.cleaning import clean_posts
from beautypulse.features import add_features
from beautypulse.analysis import save_charts, save_tables, summary_tables

parser=argparse.ArgumentParser();parser.add_argument("--input",default=str(ROOT/"data"/"sample"/"demo_posts.csv"));parser.add_argument("--output",default=str(ROOT/"data"/"processed"/"posts.csv"));args=parser.parse_args()
frame=pd.read_csv(args.input)
clean=clean_posts(frame,ROOT/"config"/"brands.csv")
featured=add_features(clean)
output=Path(args.output);output.parent.mkdir(parents=True,exist_ok=True);featured.to_csv(output,index=False,encoding="utf-8-sig")
tables=summary_tables(featured);save_tables(tables,ROOT/"reports");save_charts(featured,ROOT/"reports")
print(f"input rows: {len(frame)}");print(f"output rows: {len(featured)}");print(f"brands: {featured['brand'].nunique()}");print(f"saved: {output}")
