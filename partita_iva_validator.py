import streamlit as st
import pandas as pd
from pyVies import api
from io import BytesIO

# Initialize VIES client
vies = api.Vies()

def check_partita_iva(partita_iva: str) -> tuple:
    """
    Check the validity of an Italian Partita IVA (VAT number) and whether it starts with 'IT'.
    
    A valid Partita IVA must:
    - Be exactly 11 digits long (after removing any "IT" prefix).
    - Pass a checksum validation on the last digit.
    
    Args:
    - partita_iva (str): The Partita IVA to validate.
    
    Returns:
    - tuple: (is_valid, starts_with_IT), where
        - is_valid (bool): True if the Partita IVA is valid, False otherwise.
        - starts_with_IT (bool): True if the Partita IVA starts with 'IT', False otherwise.
    """
    # Check if the Partita IVA starts with 'IT'
    starts_with_IT = partita_iva.startswith("IT") if partita_iva else False
    
    # Remove "IT" prefix if present
    if starts_with_IT:
        partita_iva = partita_iva[2:]
    
    # Check if the Partita IVA is exactly 11 digits
    if not partita_iva or not partita_iva.isdigit() or len(partita_iva) != 11:
        return False, starts_with_IT
    
    # Calculate the checksum for validation
    even_sum = sum(int(partita_iva[i]) for i in range(0, 10, 2))
    odd_sum = sum((2 * int(partita_iva[i]) if 2 * int(partita_iva[i]) < 10 else 2 * int(partita_iva[i]) - 9)
                  for i in range(1, 10, 2))
    checksum = (even_sum + odd_sum) % 10
    control_digit = (10 - checksum) % 10
    
    # The last digit of the Partita IVA should match the control digit
    is_valid = int(partita_iva[-1]) == control_digit
    
    return is_valid, starts_with_IT

# Path to the logo file
logo_path = "assets/logo/blue-fill-text-right.svg"  # Adjust this path as needed

# Display the logo at the top of the app
st.image(logo_path, use_container_width=True)  # Automatically scales the logo to fit the app width

# Streamlit App
st.title("Partita IVA Validator and VIES Checker")

# Option 1: Upload Excel file
st.header("Upload an Excel file")
uploaded_file = st.file_uploader("Upload an Excel file containing Partita IVA values", type="xlsx")
piva_column = st.text_input("Enter the name of the column containing Partita IVA:", "fornitori.P_IVA__c")

# Option 2: Check single VAT number
st.header("Or, enter a single VAT number")
single_vat = st.text_input("Enter a single VAT number to check (e.g., IT12345678901)")
single_vat_result = {}

if single_vat and st.button("Check Single VAT"):
    is_valid, starts_with_IT = check_partita_iva(single_vat)
    if is_valid:
        try:
            vies_result = vies.request(single_vat)
            single_vat_result = {
                'countryCode': vies_result.countryCode,
                'vatNumber': vies_result.vatNumber,
                'requestDate': vies_result.requestDate,
                'valid': vies_result.valid,
                'traderName': vies_result.traderName,
                'traderCompanyType': vies_result.traderCompanyType,
                'traderAddress': vies_result.traderAddress
            }
            st.write("VIES Validation Result:", single_vat_result)
        except (api.ViesValidationError, api.ViesHTTPError, api.ViesError) as e:
            st.error(f"Error checking VAT number: {e}")
    else:
        st.error("Invalid Partita IVA format.")

# Processing uploaded Excel file
if uploaded_file:
    fornitori_raw = pd.read_excel(uploaded_file)

    if piva_column not in fornitori_raw.columns:
        st.error("The uploaded file does not contain the required '{piva_column}' column.")
    else:

        # Replace NaN values in the piva_column column with an empty string instead of dropping them
        fornitori_cleaned = fornitori_raw.copy()
        fornitori_cleaned[piva_column] = fornitori_cleaned[piva_column].fillna('')

        # Apply the check_partita_iva function to the piva_column column and add two new columns
        fornitori_cleaned[['is_valid_P_IVA', 'starts_with_IT']] = fornitori_cleaned[piva_column].apply(
            lambda x: pd.Series(check_partita_iva(x))
        )

        # Separate valid Partita IVA into "MS Code" and "VAT Number" columns
        fornitori_cleaned['MS Code'] = fornitori_cleaned.apply(lambda x: 'IT' if x['is_valid_P_IVA'] else '', axis=1)
        fornitori_cleaned['VAT Number'] = fornitori_cleaned.apply(
            lambda x: x[piva_column][2:] if x['is_valid_P_IVA'] and x['starts_with_IT'] else x[piva_column],
            axis=1
        )

        # Create a new column 'euvat' by combining 'MS Code' and 'VAT Number' for valid entries
        fornitori_cleaned['euvat'] = fornitori_cleaned.apply(
            lambda x: f"{x['MS Code']}{x['VAT Number']}" if x['is_valid_P_IVA'] else '', axis=1
        )

        # Drop duplicate entries based on the euvat column
        fornitori_unique = fornitori_cleaned.drop_duplicates(subset=['euvat'])

        fornitori_to_check = fornitori_unique.loc[fornitori_unique['is_valid_P_IVA'],:]

        # Define new columns in the DataFrame for VIES response data
        vies_columns = [
            'countryCode', 'vatNumber', 'requestDate', 'valid', 'traderName', 'traderCompanyType', 
            'traderAddress', 'traderStreet', 'traderPostcode', 'traderCity', 
            'traderNameMatch', 'traderCompanyTypeMatch', 'traderStreetMatch', 
            'traderPostcodeMatch', 'traderCityMatch', 'requestIdentifier'
        ]

        # Initialize columns with None values
        for col in vies_columns:
            fornitori_to_check[col] = None

        # Initialize VIES API client
        vies = api.Vies()

        progress_bar = st.progress(0)
        total_checks = fornitori_to_check.shape[0]

        for idx, (index, row) in enumerate(fornitori_to_check.iterrows()):
            euvat = row['euvat']
            try:
                result = vies.request(euvat)
                for col in vies_columns:
                    fornitori_to_check.at[index, col] = getattr(result, col, None)
            except (api.ViesValidationError, api.ViesHTTPError, api.ViesError) as e:
                st.write(f"Error for {euvat}: {e}")
            
            progress_bar.progress((idx + 1) / total_checks)


        # Merge VIES results back to the original fornitori_cleaned DataFrame
        fornitori_cleaned = fornitori_cleaned.merge(
            fornitori_to_check[['euvat'] + vies_columns], 
            on='euvat', 
            how='left', 
            suffixes=('', '_vies')
        )

        st.write("Validated Data with VIES Results:", fornitori_cleaned)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            fornitori_cleaned.to_excel(writer, index=False)
        output.seek(0)

        st.download_button(
            label="Download Results as Excel",
            data=output,
            file_name="validated_partita_iva.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
