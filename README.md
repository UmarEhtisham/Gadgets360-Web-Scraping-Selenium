
# Gadgets360 Mobile Phones Scraper

This project scrapes mobile phone data from Gadgets360 using Selenium and ChromeDriver. The scraper is designed to extract details of mobile phones that appear on the Gadgets360 mobile listing page.

## Overview

When you open the mobile listing page on Gadgets360, the first 20 mobile phones are displayed. To load more mobiles, you need to click the "Load More" button, which brings additional phones into view. The scraper handles this process by:

1. **Scraping the First 20 Mobiles**: Upon loading the page, the scraper extracts data from the first 20 mobile phones.
2. **Handling Pop-ups**: A pop-up may appear on the first page load. The scraper removes this pop-up to proceed with scraping.
3. **Clicking the Load More Button**: The scraper scrolls to the "Load More" button, centralizes it within the screen view area, and clicks it.
4. **Navigating Between Pages**: After clicking the "Load More" button, the next set of mobiles appears on a new tab. The scraper extracts the data, closes the tab, and returns to the main page to click the "Load More" button again, repeating the process until all data is collected.

## WebDriver Wait Implementation

To handle the loading of the "Load More" button, the following command is used to ensure the button is clickable before attempting to interact with it:

```python
load_more_button = WebDriverWait(self.driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, './/span[@class="load-more _btn"]'))
)
self.driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
```

This command does two things:
1. **Waits for the Button to be Clickable**: It waits up to 10 seconds for the "Load More" button to become clickable.
2. **Scrolls the Button into View**: It scrolls the page so that the "Load More" button is centralized in the visible screen area before clicking it.

## Prerequisites

Before running the scraper, ensure you have the following installed:
- Python 3.x
- `selenium` library
- `webdriver-manager` library
- ChromeDriver (managed automatically by `webdriver-manager`)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/web-scraping-using-selenium-gadgets360-mobiles.git
   cd web-scraping-using-selenium-gadgets360-mobiles
   ```

2. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the scraper by executing the following command:

```bash
python scraper.py
```

The scraper will start extracting data and save it to a file (e.g., CSV or JSON) based on your configuration.

## Notes

- The scraper is designed to handle pop-ups only on the first page load.
- Each "Load More" button click opens a new tab, which the scraper will close automatically after extracting data.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
