/**
 * Campaign Location Criteria Manager
 * @author Charles Bannister (shabba.io)
 * Reads campaign IDs from Google Sheet tabs and syncs location criteria to match exactly
 * Version 1.8.0
 */

// Google Ads API Query Builder Links:
// Campaign Query Builder: https://developers.google.com/google-ads/api/fields/v20/campaign_query_builder
// Geographic View Query Builder: https://developers.google.com/google-ads/api/fields/v20/geographic_view_query_builder

// CONFIGURATION
// Development Spreadsheet
// const SPREADSHEET_URL = 'https://docs.google.com/spreadsheets/d/1k3uOM-Qeha1Ma2b13a_PaLRs0eXPJeIxptI7PVvy8-k/edit?gid=1784049670#gid=1784049670';

// Production Spreadsheet
const SPREADSHEET_URL = 'https://docs.google.com/spreadsheets/d/1NKpAWeSP9Fkz_H-nSRW2_Zhelk07jt4Zkb_tWUFO9L8/edit?gid=1660336023#gid=1660336023';
// Google Sheet containing campaign tabs with location criteria to add/remove

const DEBUG_MODE = true;
// Set to true for detailed logging, false for production runs

const SEND_EMAIL_ALERT = false;
// Set to true to receive email summary when script completes

const EMAIL_RECIPIENTS = 'your-email@example.com';
// Comma-separated list of email addresses to receive alerts

const LIMIT_LOCATIONS_PER_CAMPAIGN = false;
// Set to true to limit the number of locations added per campaign

const MAX_LOCATIONS_PER_CAMPAIGN = 100;
// Maximum number of locations to add per campaign when LIMIT_LOCATIONS_PER_CAMPAIGN is true

/**
 * Main function - orchestrates the entire location criteria management process
 */
function main() {
  console.log(`Script started`);

  // Validate configuration
  validateConfiguration();

  // Get spreadsheet and process campaigns
  const spreadsheet = getSpreadsheet();
  const campaignTabs = getCampaignTabs(spreadsheet);

  // Create tabs for active campaigns that don't exist yet
  createMissingCampaignTabs(spreadsheet);

  debugLog(`Found ${campaignTabs.length} campaign tabs to process`);

  const processingSummary = [];

  // Process each campaign
  for (const tabInfo of campaignTabs) {
    console.log(`\n--- Processing Campaign ID: ${tabInfo.campaignId} ---`);

    const result = processCampaignLocationCriteria(tabInfo);
    processingSummary.push(result);
  }

  // Send email alert if configured
  if (SEND_EMAIL_ALERT) {
    sendProcessingSummaryEmail(processingSummary);
  }

  console.log(`\nScript finished`);
}

/**
 * Validates that all required configuration is properly set
 */
function validateConfiguration() {
  if (SEND_EMAIL_ALERT && EMAIL_RECIPIENTS === 'your-email@example.com') {
    throw new Error('Please update EMAIL_RECIPIENTS with actual email addresses when SEND_EMAIL_ALERT is enabled');
  }

  debugLog('Configuration validation passed');
}

/**
 * Gets the Google Spreadsheet object and validates access
 * @returns {Spreadsheet} The Google Spreadsheet object
 */
function getSpreadsheet() {
  try {
    const spreadsheet = SpreadsheetApp.openByUrl(SPREADSHEET_URL);
    console.log(`Successfully opened spreadsheet: ${spreadsheet.getName()}`);
    return spreadsheet;
  } catch (error) {
    throw new Error(`Failed to open spreadsheet. Please check the URL and permissions. Error: ${error.message}`);
  }
}

/**
 * Gets all tabs that represent campaign IDs and validates their structure
 * @param {Spreadsheet} spreadsheet - The Google Spreadsheet object
 * @returns {Array} Array of objects containing campaignId and sheet references
 */
function getCampaignTabs(spreadsheet) {
  const allSheets = spreadsheet.getSheets();
  const campaignTabs = [];

  for (const sheet of allSheets) {
    const sheetName = sheet.getName();

    // Skip sheets that don't look like campaign IDs (numbers only)
    if (!/^\d+$/.test(sheetName)) {
      debugLog(`Skipping sheet '${sheetName}' - not a valid campaign ID format`);
      continue;
    }

    // Validate sheet structure
    if (!validateSheetStructure(sheet)) {
      console.warn(`Skipping sheet '${sheetName}' - invalid structure`);
      continue;
    }

    campaignTabs.push({
      campaignId: sheetName,
      sheet: sheet
    });
  }

  if (campaignTabs.length === 0) {
    console.warn('No valid campaign tabs found in spreadsheet');
  }

  return campaignTabs;
}

/**
 * Validates that a sheet has the expected structure for location criteria management
 * @param {Sheet} sheet - The Google Sheet to validate
 * @returns {boolean} True if structure is valid
 */
function validateSheetStructure(sheet) {
  try {
    const lastRow = sheet.getLastRow();

    // Check if there's any data beyond headers
    if (lastRow < 2) {
      debugLog(`Sheet ${sheet.getName()} has no data rows`);
      return false;
    }

    return true;
  } catch (error) {
    console.warn(`Error validating sheet structure for ${sheet.getName()}: ${error.message}`);
    return false;
  }
}

/**
 * Processes location criteria for a single campaign - syncs to match desired state
 * @param {Object} tabInfo - Object containing campaignId and sheet reference
 * @returns {Object} Summary of processing results
 */
function processCampaignLocationCriteria(tabInfo) {
  const { campaignId, sheet } = tabInfo;

  const result = {
    campaignId: campaignId,
    addedCount: 0,
    removedCount: 0,
    errors: [],
    success: false
  };

  try {
    // Validate campaign exists and is enabled
    const campaign = getCampaignById(campaignId);
    if (!campaign) {
      debugLog(`Campaign with ID ${campaignId} not found or not enabled - skipping`);
      result.success = true; // Not an error, just skip
      return result;
    }

    console.log(`Found campaign: ${campaign.getName()}`);

    // Get desired location criteria from sheet
    const desiredLocationIds = getDesiredLocationIdsFromSheet(sheet);

    if (desiredLocationIds.length === 0) {
      console.log(`No desired location criteria specified for campaign ${campaignId}`);
      result.success = true;
      return result;
    }

    console.log(`Campaign ${campaignId}: ${desiredLocationIds.length} desired locations`);
    console.log(`Example desired locations: ${desiredLocationIds.slice(0, 3).join(', ')}`);

    // Get current location criteria from campaign via report
    const currentLocationIds = getCurrentLocationCriteriaFromReport(campaignId);
    console.log(`Current locations in campaign: ${currentLocationIds.length}`);

    // Calculate what needs to be added and removed
    const locationsToAdd = desiredLocationIds.filter(id => !currentLocationIds.includes(parseInt(id)));
    const locationsToRemove = currentLocationIds.filter(id => !desiredLocationIds.includes(id.toString()));

    console.log(`Locations to add: ${locationsToAdd.length}`);
    console.log(`Locations to remove: ${locationsToRemove.length}`);

    // Log examples
    if (locationsToAdd.length > 0) {
      console.log(`Example locations to add: ${locationsToAdd.slice(0, 3).join(', ')}`);
    }
    if (locationsToRemove.length > 0) {
      console.log(`Example locations to remove: ${locationsToRemove.slice(0, 3).join(', ')}`);
    }

    // Add missing location criteria
    if (locationsToAdd.length > 0) {
      result.addedCount = addLocationCriteriaToCampaign(campaign, locationsToAdd);
      console.log(`Successfully added ${result.addedCount} location criteria`);
    }

    // Remove unwanted location criteria
    if (locationsToRemove.length > 0) {
      result.removedCount = removeLocationCriteriaFromCampaign(campaign, locationsToRemove);
      console.log(`Successfully removed ${result.removedCount} location criteria`);
    }

    // Clear processed data from sheet if not in preview mode
    if (!AdsApp.getExecutionInfo().isPreview()) {
      clearProcessedDataFromSheet(sheet, { criteriaToAdd: desiredLocationIds });
      console.log(`Cleared processed data from sheet`);
    } else {
      console.log(`Preview mode - data not cleared from sheet`);
    }

    result.success = true;

  } catch (error) {
    const errorMsg = `Error processing campaign ${campaignId}: ${error.message}`;
    console.error(errorMsg);
    result.errors.push(errorMsg);
  }

  return result;
}

/**
 * Gets a campaign by its ID
 * @param {string} campaignId - The campaign ID to find
 * @returns {Campaign|null} The campaign object or null if not found
 */
function getCampaignById(campaignId) {
  try {
    const campaignIterator = AdsApp.campaigns()
      .withCondition(`campaign.id = ${campaignId}`)
      .withCondition('campaign.status = ENABLED')
      .get();

    if (campaignIterator.hasNext()) {
      return campaignIterator.next();
    }

    return null;
  } catch (error) {
    debugLog(`Error getting campaign ${campaignId}: ${error.message}`);
    return null;
  }
}

/**
 * Adds location criteria to a campaign
 * @param {Campaign} campaign - The campaign to add criteria to
 * @param {Array} criteriaIds - Array of location criteria IDs to add
 * @returns {number} Number of criteria successfully added
 */
function addLocationCriteriaToCampaign(campaign, criteriaIds) {
  if (criteriaIds.length === 0) {
    console.log('No new locations to add.');
    return 0;
  }

  // Apply location limit if enabled
  let locationsToAdd = criteriaIds;
  if (LIMIT_LOCATIONS_PER_CAMPAIGN && criteriaIds.length > MAX_LOCATIONS_PER_CAMPAIGN) {
    locationsToAdd = criteriaIds.slice(0, MAX_LOCATIONS_PER_CAMPAIGN);
    console.log(`Location limit enabled: Adding first ${MAX_LOCATIONS_PER_CAMPAIGN} of ${criteriaIds.length} locations`);
  }

  console.log(`Adding ${locationsToAdd.length} new location(s)...`);
  let addedCount = 0;
  let failedCount = 0;

  locationsToAdd.forEach(criteriaId => {
    try {
      campaign.addLocation(parseInt(criteriaId));
      addedCount++;
    } catch (error) {
      failedCount++;
      debugLog(`Failed to add location ID "${criteriaId}": ${error.message}`);
    }
  });

  if (failedCount > 0) {
    console.warn(`${failedCount} locations failed to add`);
  }

  return addedCount;
}

/**
 * Removes location criteria from a campaign by finding and removing specific criteria
 * @param {Campaign} campaign - The campaign to remove criteria from
 * @param {Array} locationIdsToRemove - Array of location criteria IDs to remove (as numbers)
 * @returns {number} Number of criteria successfully removed
 */
function removeLocationCriteriaFromCampaign(campaign, locationIdsToRemove) {
  if (locationIdsToRemove.length === 0) {
    console.log('No locations to remove.');
    return 0;
  }

  console.log(`Attempting to remove ${locationIdsToRemove.length} location(s)...`);
  let removedCount = 0;
  let failedCount = 0;

  // Convert numbers to strings for comparison (location.getId() returns strings)
  const locationIdsToRemoveAsStrings = locationIdsToRemove.map(id => id.toString());

  // Get all targeted locations
  const locationIterator = campaign.targeting().targetedLocations().get();

  if (!locationIterator.hasNext()) {
    debugLog('No locations found in campaign');
    return 0;
  }

  while (locationIterator.hasNext()) {
    const location = locationIterator.next();
    const locationId = location.getId(); // This returns a string

    if (locationIdsToRemoveAsStrings.includes(locationId)) {
      try {
        location.remove();
        removedCount++;
        // debugLog(`Removed location: ${locationId}`);
      } catch (error) {
        failedCount++;
        debugLog(`Failed to remove location ID "${locationId}": ${error.message}`);
      }
    }
  }

  if (failedCount > 0) {
    console.warn(`${failedCount} locations failed to remove`);
  }

  return removedCount;
}



/**
 * Gets desired location IDs from the sheet (Column A only)
 * @param {Sheet} sheet - The Google Sheet containing desired location data
 * @returns {Array} Array of desired location criteria IDs
 */
function getDesiredLocationIdsFromSheet(sheet) {
  const lastRow = sheet.getLastRow();
  if (lastRow < 2) {
    return [];
  }

  const range = sheet.getRange(2, 1, lastRow - 1, 1); // Get column A, skip header
  const values = range.getValues();

  const desiredLocationIds = [];

  for (let rowIndex = 0; rowIndex < values.length; rowIndex++) {
    const [locationId] = values[rowIndex];

    // Process location ID from Column A
    if (locationId && locationId.toString().trim() !== '') {
      const cleanLocationId = locationId.toString().trim();
      if (isValidCriteriaId(cleanLocationId)) {
        desiredLocationIds.push(cleanLocationId);
      } else {
        console.warn(`Row ${rowIndex + 2}: Invalid location ID: '${cleanLocationId}'`);
      }
    }
  }

  return desiredLocationIds;
}

/**
 * Gets current location criteria IDs from campaign using Google Ads report
 * @param {string} campaignId - The campaign ID to get location criteria for
 * @returns {Array} Array of current location criteria IDs as numbers
 */
function getCurrentLocationCriteriaFromReport(campaignId) {
  const query = getLocationCriteriaGaqlQuery(campaignId);
  console.log(`GAQL Query: ${query}`);

  try {
    const report = AdsApp.report(query);
    const rows = report.rows();

    debugLog(`Number of location criteria rows from query: ${rows.totalNumEntities()}`);

    if (!rows.hasNext()) {
      debugLog(`No location criteria found for campaign ${campaignId}`);
      return [];
    }

    const currentLocationIds = [];
    while (rows.hasNext()) {
      const row = rows.next();
      const locationId = parseInt(row['campaign_criterion.criterion_id']);
      currentLocationIds.push(locationId);
    }

    debugLog(`Found ${currentLocationIds.length} current location criteria`);
    return currentLocationIds;

  } catch (error) {
    console.error(`Error getting current location criteria for campaign ${campaignId}: ${error.message}`);
    console.error('Please validate the query at: https://developers.google.com/google-ads/api/fields/v20/query_validator');
    console.error('You can also use the query builder at: https://developers.google.com/google-ads/api/fields/v20/campaign_criterion_query_builder');
    return [];
  }
}

/**
 * Generates GAQL query to get location criteria for a campaign
 * @param {string} campaignId - The campaign ID to generate query for
 * @returns {string} The GAQL query string
 */
function getLocationCriteriaGaqlQuery(campaignId) {
  return `
    SELECT 
      campaign_criterion.criterion_id,
      campaign_criterion.location.geo_target_constant
    FROM campaign_criterion 
    WHERE campaign.id = ${campaignId}
      AND campaign_criterion.type = 'LOCATION'
      AND campaign_criterion.status = 'ENABLED'
  `.trim();
}

/**
 * Clears processed data from the sheet after successful operations
 * @param {Sheet} sheet - The sheet to clear data from
 * @param {Object} criteriaData - The criteria data that was processed
 */
function clearProcessedDataFromSheet(sheet, criteriaData) {
  try {
    const lastRow = sheet.getLastRow();
    if (lastRow < 2) {
      return;
    }

    const range = sheet.getRange(2, 1, lastRow - 1, 1); // Only column A, skip header
    const values = range.getValues();

    // Create new array with cleared processed data
    const clearedValues = values.map(([locationId]) => {
      const cleanLocationId = locationId ? locationId.toString().trim() : '';

      // Clear cells that were successfully processed
      const newLocationId = (cleanLocationId && criteriaData.criteriaToAdd.includes(cleanLocationId)) ? '' : locationId;

      return [newLocationId];
    });

    // Update the sheet with cleared values
    range.setValues(clearedValues);

    debugLog(`Cleared processed data from sheet ${sheet.getName()}`);
  } catch (error) {
    console.warn(`Error clearing processed data from sheet: ${error.message}`);
  }
}

/**
 * Validates if a criteria ID has the correct format
 * @param {string} criteriaId - The criteria ID to validate
 * @returns {boolean} True if the criteria ID is valid
 */
function isValidCriteriaId(criteriaId) {
  // Criteria IDs should be numeric strings
  return /^\d+$/.test(criteriaId);
}

/**
 * Sends an email summary of processing results
 * @param {Array} processingSummary - Array of processing result objects
 */
function sendProcessingSummaryEmail(processingSummary) {
  try {
    const subject = 'Location Criteria Management Summary';
    const htmlBody = generateProcessingSummaryHtml(processingSummary);

    MailApp.sendEmail({
      to: EMAIL_RECIPIENTS,
      subject: subject,
      htmlBody: htmlBody
    });

    console.log(`Email summary sent to: ${EMAIL_RECIPIENTS}`);
  } catch (error) {
    console.error(`Failed to send email summary: ${error.message}`);
  }
}

/**
 * Generates HTML content for the processing summary email
 * @param {Array} processingSummary - Array of processing result objects
 * @returns {string} HTML content for the email
 */
function generateProcessingSummaryHtml(processingSummary) {
  let html = `
    <h2>Location Criteria Management Summary</h2>
    <p><strong>Processing Date:</strong> ${new Date().toLocaleString()}</p>
    <table border="1" style="border-collapse: collapse; width: 100%;">
      <tr style="background-color: #f0f0f0;">
        <th style="padding: 8px;">Campaign ID</th>
        <th style="padding: 8px;">Added</th>
        <th style="padding: 8px;">Removed</th>
        <th style="padding: 8px;">Status</th>
        <th style="padding: 8px;">Errors</th>
      </tr>
  `;

  for (const result of processingSummary) {
    const status = result.success ? 'Success' : 'Failed';
    const statusColor = result.success ? 'green' : 'red';
    const errors = result.errors.length > 0 ? result.errors.join('<br>') : 'None';

    html += `
      <tr>
        <td style="padding: 8px;">${result.campaignId}</td>
        <td style="padding: 8px; text-align: center;">${result.addedCount}</td>
        <td style="padding: 8px; text-align: center;">${result.removedCount}</td>
        <td style="padding: 8px; color: ${statusColor}; font-weight: bold;">${status}</td>
        <td style="padding: 8px;">${errors}</td>
      </tr>
    `;
  }

  html += `
    </table>
    <p><strong>Total Campaigns Processed:</strong> ${processingSummary.length}</p>
  `;

  return html;
}

/**
 * Creates tabs for active enabled campaigns that don't exist in the spreadsheet yet
 * @param {Spreadsheet} spreadsheet - The Google Spreadsheet object
 */
function createMissingCampaignTabs(spreadsheet) {
  try {
    // Get all existing sheet names
    const existingSheetNames = spreadsheet.getSheets().map(sheet => sheet.getName());

    // Get all active enabled campaigns
    const campaignIterator = AdsApp.campaigns()
      .withCondition('campaign.status = ENABLED')
      .get();

    let createdCount = 0;

    while (campaignIterator.hasNext()) {
      const campaign = campaignIterator.next();
      const campaignId = campaign.getId().toString();

      // Skip if tab already exists
      if (existingSheetNames.includes(campaignId)) {
        continue;
      }

      // Create new tab for this campaign
      const newSheet = spreadsheet.insertSheet(campaignId);

      // Add headers
      newSheet.getRange(1, 1).setValue('Desired Location IDs');

      // Format headers
      const headerRange = newSheet.getRange(1, 1, 1, 1);
      headerRange.setFontWeight('bold');
      headerRange.setBackground('#f0f0f0');

      // Freeze header row
      newSheet.setFrozenRows(1);

      console.log(`Created tab for campaign: ${campaignId} (${campaign.getName()})`);
      createdCount++;
    }

    if (createdCount > 0) {
      console.log(`Created ${createdCount} new campaign tabs`);
    } else {
      debugLog('No new campaign tabs needed');
    }

  } catch (error) {
    console.warn(`Error creating missing campaign tabs: ${error.message}`);
  }
}

/**
 * Logs debug messages only when DEBUG_MODE is enabled
 * @param {string} message - The message to log
 */
function debugLog(message) {
  if (DEBUG_MODE) {
    console.log(`[DEBUG] ${message}`);
  }
}