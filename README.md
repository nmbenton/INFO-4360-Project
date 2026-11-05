# Flagging Scam Texts Before Customers Open Them

**INFO 4360 Complex Data Analytics, University of Denver, Fall 2026**
Team: Julia Rasul and Nicole Benton

## The problem

Almost everyone has gotten a scam text by now: a package that "couldn't be delivered," or a bank account that's suddenly "locked." 

**Why it Matters:** Americans reported losing **$470 million** to text scams in 2024 (FTC, 2025).

**Stakeholder:** the fraud team at a mobile carrier. Their job is to stop these messages before they reach customers.

**Goal:** build a fast, cheap classifier that labels each incoming text as **ham** (legitimate), **smishing** (a scam after money or personal details) or **spam** (unwanted marketing). The carrier can then block or warn on flagged texts before the customer opens them.

## Data

| | |
|---|---|
| Source | [SMS Phishing Dataset for Machine Learning and Pattern Recognition](https://data.mendeley.com/datasets/f45bkkt8pr/1) (Mishra & Soni, 2022), Mendeley Data |
| Size | 5,971 messages |
| Columns | `LABEL`, `TEXT`, plus yes/no flags `URL`, `EMAIL`, `PHONE` |
| Target | `LABEL`: ham, smishing, spam |

**Class balance (after fixing label capitalization):**

| Label | Count | Share |
|---|---:|---:|
| ham | 4,844 | 81.1% |
| smishing | 638 | 10.7% |
| spam | 489 | 8.2% |

`data/sample_messages.csv` holds a 300-row sample stratified by label. To run the full analysis, download the dataset from the Mendeley link above and save it as `data/Dataset_5971.csv`.

### Known data issues (from a first look)

- **Inconsistent labels:** the file mixes `Smishing`/`smishing` and `spam`/`Spam`. We lowercase all labels before modeling.
- **Broken characters:** the messages were converted from images found online, and 145 of them contain a garbled-character symbol (�).
- **Duplicates:** 22 message texts appear more than once. We will remove them before splitting into train and test sets so the same text can't end up in both.
- **The `URL` flag misses links:** about 55 messages flagged `URL = No` contain a link such as `smsg.io/...`. We will rebuild this flag ourselves with regex.
- **The `PHONE` flag is almost a giveaway:** only 7 of 4,844 ham messages have `PHONE = yes`, compared with 527 of 638 smishing messages. A model could score well by learning "phone number means scam," which would fail on real pharmacy or doctor's office texts. This is the main sanity check in our approach below.

## Approach (Path A: Prediction / Classification)

1. **Clean:** lowercase the labels, fix encoding, remove duplicates, rebuild the URL, email and phone flags with regex.
2. **Features:** TF-IDF on the message text, plus the flags.
3. **Models:** logistic regression, compared against Naive Bayes. Both are evaluated on a held-out test set using per-class precision and recall, because 81% of messages are ham and accuracy alone would look good even for a weak model.
4. **Interpretation:**
   - Logistic regression coefficients show which words push a text toward smishing or spam.
   - SHAP values show how much the URL, email and phone flags contribute.
5. **Sanity check:** retrain without the `PHONE` flag and test the model on smishing texts that contain no phone number.

These features are mostly **diagnostic**, because the carrier can't change what scammers write. The model's job is to **trigger a workflow**: block or warn on smishing and spam, and let ham through.

## Tools

- **Classical NLP (main approach):** regex, TF-IDF, scikit-learn. A carrier screens millions of texts a day, so the production model has to be fast and cheap.
- **Claude API, used on samples only (estimated cost under $10):**
  - **Labeling check:** relabel about 300 scam texts to test how reliable the spam vs. smishing labels are.
  - **Extraction:** pull red flags that regex misses, such as the company a text pretends to be, and test whether they're worth an API call on every new text.

## Repo structure

```
├── README.md
├── requirements.txt          # Python packages
├── data/
│   └── sample_messages.csv   # 300-row stratified sample
└── notebooks/                # analysis notebooks (Phase 2)
```

## How to run

*Coming in Phase 2.* The plan:

```
git clone <this repo>
pip install -r requirements.txt
```

Then download the full dataset into `data/` (see above) and run the notebooks in order.

## Status

- [x] Phase 1: problem, data and proposal
- [ ] Phase 2: modeling and analysis
- [ ] Final presentation and report

## References

Federal Trade Commission. (2025, April 16). *New FTC data show top text message scams of 2024; overall losses to text scams hit $470 million* [Press release]. https://www.ftc.gov/news-events/news/press-releases/2025/04/new-ftc-data-show-top-text-message-scams-2024-overall-losses-text-scams-hit-470-million

Mishra, S., & Soni, D. (2022). *SMS Phishing Dataset for Machine Learning and Pattern Recognition* (Version 1) [Data set]. Mendeley Data. https://data.mendeley.com/datasets/f45bkkt8pr/1
