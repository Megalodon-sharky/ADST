# Data Cleaning: Google Year in Search (`trends.csv`)

Cleaning of the Google Year in Search dataset for ADST. The notebook takes the
raw file, fixes what is broken and exports a dataset that is safe to analyse.

## Files

| File | Description |
|------|-------------|
| `trends.csv` | Original dataset. 26,955 rows, 5 columns |
| `trends_cleaned.csv` | Cleaned dataset. 26,945 rows, 7 columns |
| `trends_data_cleaning.ipynb` | Notebook with all code, outputs and explanations |

## Dataset

Google Year in Search rankings covering 83 locations and the years 2001 to 2020.
Each row is one entry in a top-5 list, keyed by location, year, category and rank.

## Cleaning steps

**1. Import.** Loaded with pandas. No parser errors, which matters because some
queries contain commas and embedded quote characters such as `Toys "R" Us`. A
copy of the raw frame was kept so every step could be compared against it.

**2. Missing values.** None found. Checked for nulls stored as empty strings,
whitespace-only strings and placeholder text (`NA`, `null`, `-`, `unknown`), and
those were zero too. No action taken. The file is a published ranking rather than
raw collected data, so no value had the chance to go missing.

**3. Duplicates.** 10 duplicated rows removed, leaving 26,945.

They were not scattered. They formed two complete top-5 blocks, each stored
twice: Kazakhstan 2018 (`Жылдың фильмі/Фильм года`) and Kenya 2020
(`Trending How To  (Tech)`). Two whole blocks repeated cleanly points at an
append error during file assembly rather than data-entry noise. The rows matched
on all five columns, so dropping them lost nothing.

**4. Inconsistent entries.** Three separate problems.

*Whitespace.* 175 category values had leading or trailing spaces, 25 had internal
double spaces and 4 query values did too. Stripping and collapsing removed 7
phantom categories that existed only because of spacing.

*Category language sprawl.* The main problem in this dataset. 2,443 distinct
category labels against 83 locations, with 87 percent appearing in only one
country, because each country recorded its labels in its own language. `Movies`
and `Películas` were stored as separate categories, as were `Athletes` and
`Deportistas`, and `How to...` and `Cómo`. A new `category_standard` column maps
raw labels to 24 standard English labels using keyword rules rather than a
2,443-entry lookup table. Coverage is 55.6 percent of rows. The rest keeps
`Unmapped`. The original `category` column is preserved unchanged.

*Capitalisation.* 76 category and 446 query values differ from another value only
by case. Left alone deliberately. Case carries meaning in search terms, `Apple`
and `apple` are different queries, and `category_standard` already solves the
grouping problem by lowercasing internally before matching.

**5. Data types.**

| Column | Before | After | Reason |
|--------|--------|-------|--------|
| `location` | object | category | 83 distinct values against 26,945 rows |
| `category` | object | category | 2,443 distinct values |
| `category_standard` | new | category | 25 distinct values |
| `query` | object | string | correct dtype for text |
| `year` | int64 | int16 | range 2001-2020 fits easily |
| `rank_position` | int64 | ordered categorical 1-5 | see below |

`rank` was cast to an **ordered categorical** rather than left as an integer. As
an integer, `df['rank'].mean()` returns exactly 3.0 and looks like a finding,
when rank is an ordinal position whose mean is fixed by construction. The ordered
categorical keeps sorting and comparison working while making that arithmetic
impossible.

**6. Column names.** One rename. `rank` to `rank_position`, because `rank` is
also a `DataFrame` method, so `df.rank` returns the method instead of the column.
The other four names were already lowercase, descriptive and space-free.

Also added `is_global`, a boolean flag. `location` mixes two levels of
granularity: `Global` is an aggregate sitting in the same column as 82 real
countries, so `groupby('location')` double-counts. Filter with `df[~df.is_global]`
for country-level analysis.

**7. Formatting.** All checks return zero after step 4: no stray whitespace, no
double spaces, no empty strings, no year outside 2001-2020, no rank outside 1-5.
Columns reordered so identifiers come first and the query last. Rows sorted by
location, year, category and rank.

**8. Verification.** The dataset follows one structural rule: every combination
of location, year and category should hold exactly five rows, ranked 1 to 5.
After cleaning, all 5,389 groups hold exactly five rows and no group repeats a
rank. Before cleaning, two groups held ten. This confirms the duplicate removal
took out the right rows and nothing else.

## Result

| Metric | Raw | Cleaned |
|--------|-----|---------|
| Rows | 26,955 | 26,945 |
| Columns | 5 | 7 |
| Missing values | 0 | 0 |
| Duplicate rows | 10 | 0 |
| Groups not holding exactly 5 rows | 2 | 0 |

## Known limit

44 percent of rows keep `Unmapped` in `category_standard`. The remaining category
labels are written in Arabic, Ukrainian, Thai, Hebrew, Korean and other scripts
the keyword rules do not cover. Guessing translations to raise the coverage number
would put wrong labels into the data. The original `category` column is unchanged,
so the mapping can be extended later without redoing any of this work.

## Reproducing

Put `trends.csv` in the same folder as the notebook and run all cells. Requires
`pandas` and `numpy`.
