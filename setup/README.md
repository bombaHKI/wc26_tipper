# Setting Up a New Competition

When creating a new competition (e.g. a new World Cup, Euros, etc.), the following setup steps must be completed in order.

## 1. Configure the Football API

Ensure that the API configuration in `config.py` points to the correct competition and contains a valid API key.

Example:

```python
apiJson = {
    "base-url": "...",
    "headers": {
        ...
    }
}
```

Verify that the configured competition returns the expected teams and matches before proceeding.

---

## 2. Add Teams to the Database

Populate the `teams` table in `data/adatok.sqlite` using the Football API.

This can be done through the provided setup scripts or any existing import mechanism.

After completion, verify that all participating teams have been added correctly.

---

## 3. Import Matches

Once all teams exist in the database, import the fixtures for the competition.

You can do this in either of the following ways:

### Option A – Admin UI

Navigate to the administration interface and run **Update Matches**.

### Option B – Script / Code

Execute the match update functionality directly from code.

This step downloads all fixtures from the Football API and stores them in the database.

After completion, verify that:

* All group-stage matches are present
* Match dates and times are correct

---

## 4. Download Team Flags

Download the country flags used by the frontend.

From the project root directory, run:

```bash
python -m setup.download_svg
```

The script will:

* Retrieve all teams from the Football API
* Determine the corresponding country code
* Download the SVG flag from FlagCDN
* Save the file to:

```text
static/media/csapatok/
```

Each flag is stored using the team's ID:

```text
static/media/csapatok/
├── 1.svg
├── 2.svg
├── 3.svg
└── ...
```

---

## 5. Verification Checklist

Before opening the competition to users, verify that:

* [ ] API configuration points to the correct competition
* [ ] All teams were imported into `data/adatok.sqlite`
* [ ] All fixtures were imported successfully
* [ ] Team flags exist in `static/media/csapatok`
* [ ] Team names and flags match correctly
* [ ] Match dates and kickoff times are correct
* [ ] The competition appears correctly in the UI
