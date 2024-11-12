
# Partita IVA Validator and VIES Checker

This Streamlit app allows users to validate Italian Partita IVA (VAT) numbers, check their validity using a checksum, and verify the VAT numbers through the EU's VIES (VAT Information Exchange System). It supports both individual VAT checks and batch processing of VAT numbers from an uploaded Excel file.

## Features

- **Single VAT Check**: Enter a single Partita IVA (e.g., `IT12345678901`) to verify its validity and retrieve company information from VIES.
- **Batch VAT Check**: Upload an Excel file containing Partita IVA numbers to perform batch validation and VIES checks.
- **Customizable VAT Column**: Specify the column name in the uploaded Excel file that contains Partita IVA numbers.
- **Progress Monitoring**: A progress bar displays the status of the batch validation process.
- **Downloadable Results**: Export the validation results, including VIES information, as an Excel file.

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/gabboDTD/vat-vies-checker
   cd partita-iva-validator
   ```

2. **Install Poetry** (if not already installed)
   Follow the instructions [here](https://python-poetry.org/docs/#installation) to install Poetry.

3. **Install Dependencies**
   ```bash
   poetry install
   ```

4. **Run the App**
   ```bash
   poetry run streamlit run app.py
   ```

## Usage

### 1. Single VAT Number Validation
   - Enter a Partita IVA in the text input field.
   - Click the "Check Single VAT" button to validate it and, if valid, query the VIES database for company information.

### 2. Batch Validation with Excel File
   - Upload an Excel file containing Partita IVA numbers.
   - Specify the name of the column containing the Partita IVA numbers.
   - The app validates each VAT number and fetches VIES data for valid entries, showing progress during processing.
   - Download the results as an Excel file after the validation completes.

### Excel Output Format
The output file contains the following columns:
- Original VAT number data (from the uploaded file)
- Validation status and country code (for valid entries)
- VIES response fields (e.g., company name, address) for successfully validated VAT numbers

## Requirements

- **Python 3.7+**
- **Poetry**: For dependency management and virtual environment handling

## Folder Structure

- `partita_iva_validator.py`: The main application file for running the Streamlit app.
- `README.md`: Documentation for the project.
- `pyproject.toml`: Project metadata and dependency management configuration for Poetry.

## Notes

- This app uses the VIES API, which may have rate limits. Consider limiting the number of API calls by processing unique VAT numbers only.
- A stable internet connection is required for VIES checks.

## License

This project is licensed under the **GNU Affero General Public License v3 (AGPL-3.0)**. 

By using, modifying, or distributing this software, you agree to the terms of the AGPL v3. This license enforces that:
- Any modifications or derivative works must also be open-sourced under the same AGPL v3 license if distributed.
- If the software is used over a network, such as in a web application, the source code, including any modifications, must be made available to users.

For more information, refer to the full text of the AGPL v3 in the `LICENSE` file included with this repository, or visit the [GNU website](https://www.gnu.org/licenses/agpl-3.0.html) to read the license terms.

## Author

Developed by [Gabriele Spina](https://github.com/gabboDTD).
