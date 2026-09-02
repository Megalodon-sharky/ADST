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

Google Year in Search rankings across 83 locations and the years 2001 to 2020.
Each row is one entry in a top-5 list, keyed by location, year, category and
rank.

## Cleaning steps

### 1. Import

Loaded with pandas. No parser errors, which matters more than it sounds here.
Some queries hold commas inside them and at least one holds embedded quote
characters, `Toys "R" Us`. Broken quoting would split that row on the internal
comma, find six fields where five were expected and throw a tokenising error.
It did not. A copy of the raw frame was kept so every later step could be
checked against the original.

### 2. Missing values

None. Zero nulls across all five columns.

A zero can also mean the nulls are wearing a disguise, so the notebook checks
for empty strings, whitespace-only strings and placeholder text such as `NA`,
`null`, `-` and `unknown`. Those came back zero too.

No action taken. The file is a published ranking rather than raw collected data,
so no value ever had the chance to go missing. Imputing here would invent data.

### 3. Duplicates

10 rows removed, leaving 26,945.

They were not scattered. They formed two complete top-5 blocks, each stored
twice: Kazakhstan 2018 (`Жылдың фильмі/Фильм года`) and Kenya 2020
(`Trending How To  (Tech)`).

The shape of the fault points at the cause. Ten random duplicate rows would mean
sloppy data entry. Two whole top-5 lists repeated cleanly means the file was
assembled by appending per-country blocks and two of them went in twice. That is
an ingestion error rather than a data error, which is good news, because the
repeated rows matched on all five columns and dropping them lost nothing.

### 4. Inconsistent entries

Three separate problems, in the order they had to be fixed.

**Whitespace first.** 175 category values carried leading or trailing spaces, 25
had internal double spaces and 4 query values did too. Stripping and collapsing
removed 7 phantom categories that existed only because of spacing. This has to
run first, because stray whitespace inflates every unique count, which means any
later deduplication of meaning would start from a wrong number.

**Then the category labels.** This is the real problem in the dataset. 2,443
distinct labels against 83 locations, and 87 percent of them appear in exactly
one country.

The counts give the cause away. `Movies` has 330 rows. `Películas`, the same
word in Spanish, sits in a separate group with 250. `Athletes` and `Deportistas`
are one concept. So are `How to...` and `Cómo`. Each country recorded its labels
in its own language, which means one concept splits across many strings, which
means `groupby('category')` returns over two thousand groups and every
cross-country comparison built on it is meaningless.

A new `category_standard` column fixes this. A hand-written lookup table would
need 2,443 entries, so the notebook uses keyword rules instead, matching each
raw label against patterns covering the main concepts across the languages
present. 2,443 labels collapse to 24 standard ones covering 55.6 percent of
rows. The original `category` column is left untouched beside it.

**Capitalisation last, and deliberately left alone.** 76 category values and 446
query values differ from some other value only by case. Case carries meaning in
search terms. `Apple` the company and `apple` the fruit are different queries,
and a brand like `iPhone` would be damaged by forcing it. `category_standard`
already lowercases internally before matching, so case blocks nothing. Folding
it in the raw columns would destroy information to fix a problem that is already
solved.

### 5. Data types

| Column | Before | After | Reason |
|--------|--------|-------|--------|
| `location` | object | category | 83 distinct values against 26,945 rows |
| `category` | object | category | 2,443 distinct values |
| `category_standard` | new | category | 25 distinct values |
| `query` | object | string | correct dtype for text |
| `year` | int64 | int16 | range 2001-2020 fits easily |
| `rank_position` | int64 | ordered categorical 1-5 | see below |

The rank cast is the one worth explaining. Left as an integer,
`df['rank'].mean()` returns exactly 3.0 and looks like a result. It is not.
Rank is an ordinal position and every block holds one of each value 1 through 5,
so that mean is fixed by construction and would come out at 3.0 on any correctly
built file. An ordered categorical keeps sorting and comparison working while
making the meaningless arithmetic impossible.

### 6. Column names

One rename. `rank` became `rank_position`, because `rank` is also a `DataFrame`
method, so `df.rank` hands back the method instead of the column and only
`df['rank']` works. That is a real trap during analysis. The other four names
were already lowercase, descriptive and free of spaces, so renaming them would
be churn.

One column added. `location` was mixing two levels of granularity, with `Global`
sitting as an aggregate in the same column as 82 real countries, which means
`groupby('location')` counts every global row twice. Nothing in the raw data
marks it as different, which is exactly how this kind of bug survives into
published results. `is_global` makes it explicit. Filter with `df[~df.is_global]`
for country-level work.

### 7. Formatting

Every check returns zero after step 4. No stray whitespace, no double spaces, no
empty strings, no year outside 2001 to 2020, no rank outside 1 to 5. Columns
reordered so the identifiers come first and the query last. Rows sorted by
location, year, category and rank.

### 8. Verification

The dataset follows one structural rule. Every combination of location, year and
category should hold exactly five rows, ranked 1 to 5.

After cleaning, all 5,389 groups hold exactly five rows and no group repeats a
rank. Before cleaning, two groups held ten. This check was built on a completely
different idea from `duplicated()` and it came at the file from the other end,
so the two methods agreeing is much stronger evidence than either one alone.

## Result

| Metric | Raw | Cleaned |
|--------|-----|---------|
| Rows | 26,955 | 26,945 |
| Columns | 5 | 7 |
| Missing values | 0 | 0 |
| Duplicate rows | 10 | 0 |
| Groups not holding exactly 5 rows | 2 | 0 |

## Known limit

44 percent of rows keep `Unmapped` in `category_standard`. The remaining labels
are written in Arabic, Ukrainian, Thai, Hebrew, Korean and other scripts the
keyword rules do not cover.

Guessing translations to push that number up would put wrong labels into the
data, and a confident wrong label is worse than an honest gap. The original
`category` column is unchanged, so the rules can be extended later without
redoing any of this work.

## Reproducing

Put `trends.csv` in the same folder as the notebook and run all cells. Needs
`pandas` and `numpy`.
