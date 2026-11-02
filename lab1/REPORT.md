# Lab 1 report

## Implemented variants

- Airports: `airports-csv | title | clean | words-all | top10 | mark | boost`
- Artworks: `artworks-csv | title | clean | words-all | ranked | mark | none`

Run the airports variant with `python main.py` from this directory. Run the artworks variant with `python main.py --variant artworks`.

## Text normalization

For `clean`, text is case-folded, decomposed with Unicode NFKD, stripped of combining diacritics, and split into alphanumeric words. The same normalization is applied to the query and titles. Punctuation therefore acts as a word separator, and accented and unaccented spellings compare equally.

## Search and relevance

`words-all` matches a record only when every distinct normalized query word appears in its title. Relevance is the sum of the occurrences of those query words in the title. Results are sorted by descending final score, then descending relevance, then title alphabetically. An empty query matches every record that passes the filters with relevance zero.

The airports variant displays at most ten matching records. The artworks variant displays every match.

## Ratings and highlighting

Airports ratings are kept in memory by record ID until another file is loaded or the program exits. The boost is `rating × 0.5`; final score is `relevance + boost`. Ratings affect ordering only and cannot make a non-match appear. `rate` accepts records from the most recently displayed results.

In both variants, matching title words are wrapped in `[[double brackets]]`. Other record fields are displayed but are not searched or highlighted because both assigned variants use the `title` field.
