# Campaign Zip Code Sync

## Core Steps

1. **Data Retrieval:** Get zip code data from an API endpoint.
   - The API updates every 15 minutes.
2. **Data Filtering:** Select zip codes where `max_call_price` is greater than 20.
3. **Campaign Targeting:** Only target enabled Google Ads campaigns.
4. **Location Sync:**
   - Remove zip codes from campaigns if they're not in the latest data.
   - Add new zip codes from the data to campaigns (get the location ID based on the zip code first)
5. **Reporting:** Log runs to a new slack channel (muted)
6. **Notifications:** Send Slack notifications to the admin for any problems.

---

## Notes/Specifics

- **Execution Frequency:** Every 15 minutes.

### Endpoint

```
https://www.elocal.com/api/call_category_price_list/149.json?api_key=c13b178aca3cd7d642b6b1e4fe22f1bb
```

---

## Python Setup

1. Create a virtual environment:
   ```sh
   python3 -m venv .venv
   ```
2. Activate the virtual environment:
   ```sh
   source .venv/bin/activate
   ```
3. Install Poetry using pip:
   ```sh
   pip install poetry
   ```
4. Initialize Poetry in the project:
   ```sh
   poetry init
   # Follow the prompts, or use 'poetry init --no-interaction' for defaults
   ```
5. Install dependencies from poetry.lock/pyproject.toml:
   ```sh
   poetry install
   ```

## Running Tests

To run the tests, use:

```
pytest
```
