# Flagging Scam Texts Before Customers Open Them

**INFO 4360 Complex Data Analytics, University of Denver, Fall 2026**
Team: Julia Rasul and Nicole Benton

## The problem

Almost everyone has gotten a scam text by now: a package that "couldn't be delivered," or a bank account that's suddenly "locked."

**Why it Matters:** Americans reported losing **$470 million** to text scams in 2024 (FTC, 2025).

**Stakeholder:** the fraud team at a mobile carrier. Their job is to stop these messages before they reach customers.

**Goal:** build a fast, cheap classifier that labels each incoming text as **ham** (legitimate), **smishing** (a scam after money or personal details) or **spam** (unwanted marketing). The carrier can then block or warn on flagged texts before the customer opens them.

## Main results

| Model (test set: 1,167 texts, 200 scams) | Accuracy | Scam precision | Scam recall | Scam F1 |
|---|---:|---:|---:|---:|
| Baseline: always predict ham | 0.829 | n/a | 0.000 | 0.000 |
| Model A: Naive Bayes (words) | 0.966 | 0.982 | 0.815 | 0.891 |
| Model B: Logistic regression (words + 10 text signals) | 0.980 | 0.978 | 0.905 | 0.940 |
| **Model C: Balanced logistic regression (final)** | **0.983** | **0.955** | **0.945** | **0.950** |

- **Scam texts are structurally different from real ones.** About 3 in 4 scams ask the reader to call, text, reply or click, compared with fewer than 1 in 10 real texts. Scams average about 15 digits per message, compared with 0.3 for real texts.
- **The text signals caught more scams.** Adding them to the word features raised scam recall from 0.815 to 0.945.
- **The model doesn't rely on phone numbers.** With all phone and digit information removed, it still reaches an F1 of 0.905.
- **The model is ready to drive a block/warn workflow.** At a 95% cutoff it blocks 173 of 200 test scams and zero real texts. It caught all 108 smishing texts in the test set; every scam it missed was marketing spam.
- **Biggest limitation:** the data is older and comes mostly from the UK and India, so the model should be retrained on current U.S. texts before real use.


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

After removing duplicates and combining spam and smishing, 17.1% of messages are scams.

The full dataset is included in the repo at `data/Dataset_5971.csv`, so no download is needed. It can also be downloaded from the Mendeley link above.

### Data issues and how we handled them

- **Inconsistent labels:** the file mixes `Smishing`/`smishing` and `spam`/`Spam`. We lowercase all labels.
- **Placeholder and HTML codes:** some texts contain `&lt;#&gt;` and other HTML codes. We replace the placeholder and decode the HTML.
- **Broken characters:** the messages were converted from images found online, and 145 contain a garbled-character symbol (�). Some texts are also cut off partway through. We left these as they are and list them as a limitation.
- **Duplicates:** there are 95 exact duplicate rows and 140 repeated message texts. We removed all 140 repeats before splitting, so the same text can't end up in both the training and test sets.
- **The `URL` flag misses links:** about 55 messages flagged `URL = No` contain a link. We don't use the original flags; we rebuild link, phone number and short code detection with regex in `src/scamfeatures.py`.
- **The `PHONE` flag is almost a giveaway:** only 7 of 4,844 ham messages have `PHONE = yes`, compared with 527 of 638 smishing messages. To check that the model doesn't just learn "phone number means scam," we retrained it with no phone or digit information (see results above).

## Approach (Path A: Prediction / Classification)

1. **Clean:** lowercase the labels, replace placeholder and HTML codes, trim spaces, remove duplicate texts, and combine spam and smishing into one "scam" class.
2. **Split:** 80/20 train/test split, stratified so both sets keep a 17.1% scam share.
3. **Features:**
   - TF-IDF scores for 3,465 words, learned from the training texts only.
   - 10 text signals from Phase 2: word count, digits, phone number, short code, link, currency symbol, capital letters, exclamation points, call to action, and VADER sentiment.
4. **Models:**
   - A majority class baseline.
   - Naive Bayes on words only.
   - Logistic regression on words plus signals, both plain and with balanced class weights.
   - Models are compared on accuracy, scam precision, recall and F1, training vs. test scores, and 5-fold cross validation.
5. **Interpretation:** logistic regression coefficients show which words and signals push a text toward scam.
6. **Sanity check:** we retrained the final model without phone, digit or short code information, and tested it on scams that contain no phone number.

The features are mostly **diagnostic**, because the carrier can't change what scammers write. The model's job is to **trigger a workflow**:
- **Block** at a 95% or higher chance of scam.
- **Warn** between 50% and 95%.
- **Deliver** below 50%.

## Tools

- **Classical NLP:** pandas, regex, scikit-learn (TF-IDF, Naive Bayes, logistic regression), VADER sentiment, matplotlib and wordcloud. A carrier screens millions of texts a day, so the model has to be fast, cheap and explainable.
- **No LLM in the model.** In Phase 1 we planned to use the Claude API to check the spam vs. smishing labels. Phase 2 showed the two classes are nearly identical, so we combined them and dropped that step.
- **API cost: $0** (no API calls). We used Claude only as a coding and writing assistant; it did not label, classify or generate any data. Details are in the AI usage log at the end of the final report.

## Repo structure

```
├── README.md
├── requirements.txt                      # Python packages
├── LICENSE
├── .gitignore
├── data/
│   └── Dataset_5971.csv                  # full dataset
├── src/
│   └── scamfeatures.py                   # text signal features shared by the model and Scam Checker
├── models/
│   └── scam_model.joblib                 # trained final model (created by the final report notebook)
└── notebooks/
    ├── Final_Report.ipynb                # Phase 3 final report (start here)
    ├── Final_Report.html                 # HTML export of the final report
    ├── Scam_Checker.ipynb                # type a message, get the chance it's a scam
    ├── Complex_Project_Phase_3_V1.ipynb  # Phase 3 modeling draft
    ├── Complex Project V2.ipynb          # Phase 2 analysis
    └── Complex Project.ipynb             # earlier version
```

## How to run

1. Clone the repo:
   ```
   git clone https://github.com/nmbenton/INFO-4360-Project.git
   cd INFO-4360-Project
   ```
2. Install the requirements (tested with Python 3.13):
   ```
   pip install -r requirements.txt
   ```
3. Open `notebooks/Final_Report.ipynb` and run all cells. This trains the models, prints all results and saves the final model to `models/scam_model.joblib`.
4. Optional: open `notebooks/Scam_Checker.ipynb`, run the cells and type any message to see its chance of being a scam. This notebook needs the saved model from step 3.

Run the notebooks from inside the `notebooks/` folder, since they load `../data/Dataset_5971.csv` and `../src/scamfeatures.py`. No API key is needed.

To view the results without running anything, open `notebooks/Final_Report.html` in a browser.

## Status

- [x] Phase 1: problem, data and proposal
- [x] Phase 2: data exploration and text mining
- [x] Phase 3: modeling and interpretation
- [x] Final presentation and report

## References

Federal Trade Commission. (2025, April 16). *New FTC data show top text message scams of 2024; overall losses to text scams hit $470 million* [Press release]. https://www.ftc.gov/news-events/news/press-releases/2025/04/new-ftc-data-show-top-text-message-scams-2024-overall-losses-text-scams-hit-470-million

Hutto, C. J., & Gilbert, E. (2014). VADER: A parsimonious rule-based model for sentiment analysis of social media text. *Proceedings of the International AAAI Conference on Web and Social Media, 8*(1).

Mishra, S., & Soni, D. (2022). *SMS Phishing Dataset for Machine Learning and Pattern Recognition* (Version 1) [Data set]. Mendeley Data. https://data.mendeley.com/datasets/f45bkkt8pr/1

Mishra, S., & Soni, D. (2022). *SMS Phishing Dataset for Machine Learning and Pattern Recognition* (Version 1) [Data set]. Mendeley Data. https://data.mendeley.com/datasets/f45bkkt8pr/1
