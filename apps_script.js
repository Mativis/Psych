/**
 * Automatic Thoughts Record (RPA) - Google Sheets API
 * 
 * Instructions:
 * 1. Open a Google Sheet.
 * 2. Click Extensions > Apps Script.
 * 3. Delete any code in Code.gs and paste this code.
 * 4. Change the API_KEY below to a secure secret.
 * 5. Run the `setupSheets` function once manually to initialize sheets.
 * 6. Click Deploy > New Deployment.
 *    - Select type: "Web app"
 *    - Execute as: "Me" (your-email@gmail.com)
 *    - Who has access: "Anyone"
 * 7. Copy the Web App URL and paste it in the Streamlit configurations.
 */

// CHANGE THIS TO A SECURE API KEY
const API_KEY = "RPA_SECRET_SECURE_TOKEN_2026";

/**
 * Common response helper to return JSON.
 */
function jsonResponse(data, status = 200) {
  return ContentService.createTextOutput(JSON.stringify(data))
    .setMimeType(ContentService.MimeType.JSON);
}

/**
 * SHA-256 Hashing helper inside Apps Script
 */
function hashString(str) {
  const digest = Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, str, Utilities.Charset.UTF_8);
  let hash = "";
  for (let i = 0; i < digest.length; i++) {
    let byteVal = digest[i];
    if (byteVal < 0) byteVal += 256;
    let byteString = byteVal.toString(16);
    if (byteString.length == 1) byteString = "0" + byteString;
    hash += byteString;
  }
  return hash;
}

/**
 * Setup sheets if they don't exist. Can be run manually or triggered.
 */
function setupSheets() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  
  // 1. Users sheet
  let usersSheet = ss.getSheetByName("users");
  if (!usersSheet) {
    usersSheet = ss.insertSheet("users");
    usersSheet.appendRow(["username", "password_hash", "role", "mediator", "created_at"]);
    usersSheet.getRange("A1:E1").setFontWeight("bold").setBackground("#d9ead3");
  }
  
  // 2. Records sheet
  let recordsSheet = ss.getSheetByName("records");
  if (!recordsSheet) {
    recordsSheet = ss.insertSheet("records");
    recordsSheet.appendRow(["id", "patient", "date_local", "situation", "thought", "emotion", "behavior", "timestamp"]);
    recordsSheet.getRange("A1:H1").setFontWeight("bold").setBackground("#c9daf8");
  }
  
  // Insert default admin if users sheet is empty (only has header)
  if (usersSheet.getLastRow() === 1) {
    // default credentials: admin / admin123
    const adminUser = "admin";
    const passwordHash = hashString(adminUser + "admin123");
    usersSheet.appendRow([adminUser, passwordHash, "Admin", "", new Date().toISOString()]);
  }
  
  return { success: true, message: "Sheets setup successfully with a default Admin ('admin' / 'admin123')" };
}

/**
 * Handle GET requests.
 */
function doGet(e) {
  try {
    const params = e.parameter;
    
    // Check API Key
    if (!params.apiKey || params.apiKey !== API_KEY) {
      return jsonResponse({ success: false, error: "Unauthorized: Invalid API Key" }, 401);
    }
    
    const action = params.action;
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    
    if (action === "setup") {
      const res = setupSheets();
      return jsonResponse(res);
    }
    
    if (action === "getUsers") {
      const sheet = ss.getSheetByName("users");
      if (!sheet) return jsonResponse({ success: false, error: "Users sheet not initialized. Run setup action." });
      
      const data = sheet.getDataRange().getValues();
      const headers = data[0];
      const users = [];
      
      for (let i = 1; i < data.length; i++) {
        const row = data[i];
        users.push({
          username: row[0],
          role: row[2],
          mediator: row[3],
          created_at: row[4]
        });
      }
      return jsonResponse({ success: true, users: users });
    }
    
    if (action === "getMediators") {
      const sheet = ss.getSheetByName("users");
      if (!sheet) return jsonResponse({ success: false, error: "Users sheet not initialized." });
      
      const data = sheet.getDataRange().getValues();
      const mediators = [];
      for (let i = 1; i < data.length; i++) {
        if (data[i][2] === "Mediador") {
          mediators.push(data[i][0]);
        }
      }
      return jsonResponse({ success: true, mediators: mediators });
    }
    
    if (action === "login") {
      const username = params.username;
      const passHash = params.passwordHash; // Streamlit sends hashed password
      
      const sheet = ss.getSheetByName("users");
      if (!sheet) return jsonResponse({ success: false, error: "Users sheet not initialized." });
      
      const data = sheet.getDataRange().getValues();
      for (let i = 1; i < data.length; i++) {
        if (data[i][0].toLowerCase() === username.toLowerCase()) {
          if (data[i][1] === passHash) {
            return jsonResponse({ 
              success: true, 
              user: {
                username: data[i][0],
                role: data[i][2],
                mediator: data[i][3]
              } 
            });
          } else {
            return jsonResponse({ success: false, error: "Senha incorreta." });
          }
        }
      }
      return jsonResponse({ success: false, error: "Usuário não encontrado." });
    }
    
    if (action === "getPatientRecords") {
      const patient = params.patient;
      const sheet = ss.getSheetByName("records");
      if (!sheet) return jsonResponse({ success: false, error: "Records sheet not initialized." });
      
      const data = sheet.getDataRange().getValues();
      const records = [];
      for (let i = 1; i < data.length; i++) {
        if (data[i][1].toLowerCase() === patient.toLowerCase()) {
          records.push({
            id: data[i][0],
            patient: data[i][1],
            date_local: data[i][2],
            situation: data[i][3],
            thought: data[i][4],
            emotion: data[i][5],
            behavior: data[i][6],
            timestamp: data[i][7]
          });
        }
      }
      return jsonResponse({ success: true, records: records });
    }
    
    if (action === "getMediatorPatients") {
      const mediator = params.mediator;
      const usersSheet = ss.getSheetByName("users");
      const recordsSheet = ss.getSheetByName("records");
      
      if (!usersSheet || !recordsSheet) {
        return jsonResponse({ success: false, error: "Sheets not initialized." });
      }
      
      // Get all patients of this mediator
      const usersData = usersSheet.getDataRange().getValues();
      const patients = [];
      for (let i = 1; i < usersData.length; i++) {
        if (usersData[i][2] === "Paciente" && usersData[i][3].toLowerCase() === mediator.toLowerCase()) {
          patients.push(usersData[i][0]);
        }
      }
      
      // Get all records of these patients
      const recordsData = recordsSheet.getDataRange().getValues();
      const patientRecords = {};
      
      // Pre-initialize empty arrays for patients
      patients.forEach(p => {
        patientRecords[p] = [];
      });
      
      for (let i = 1; i < recordsData.length; i++) {
        const patientName = recordsData[i][1];
        // Check case insensitively but group matching the correct patient case in our list
        const matchedPatient = patients.find(p => p.toLowerCase() === patientName.toLowerCase());
        if (matchedPatient) {
          patientRecords[matchedPatient].push({
            id: recordsData[i][0],
            patient: patientName,
            date_local: recordsData[i][2],
            situation: recordsData[i][3],
            thought: recordsData[i][4],
            emotion: recordsData[i][5],
            behavior: recordsData[i][6],
            timestamp: recordsData[i][7]
          });
        }
      }
      
      return jsonResponse({ 
        success: true, 
        patients: patients,
        records: patientRecords
      });
    }
    
    return jsonResponse({ success: false, error: "Action not recognized." }, 400);
    
  } catch (error) {
    return jsonResponse({ success: false, error: error.toString() }, 500);
  }
}

/**
 * Handle POST requests.
 */
function doPost(e) {
  try {
    const postData = JSON.parse(e.postData.contents);
    
    // Check API Key
    if (!postData.apiKey || postData.apiKey !== API_KEY) {
      return jsonResponse({ success: false, error: "Unauthorized: Invalid API Key" }, 401);
    }
    
    const action = postData.action;
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    
    if (action === "createUser") {
      const username = postData.username;
      const passwordHash = postData.passwordHash;
      const role = postData.role;
      const mediator = postData.mediator || "";
      
      const sheet = ss.getSheetByName("users");
      if (!sheet) return jsonResponse({ success: false, error: "Users sheet not initialized." });
      
      // Check if user already exists
      const data = sheet.getDataRange().getValues();
      for (let i = 1; i < data.length; i++) {
        if (data[i][0].toLowerCase() === username.toLowerCase()) {
          return jsonResponse({ success: false, error: "Usuário já existe." });
        }
      }
      
      // Append new user
      sheet.appendRow([username, passwordHash, role, mediator, new Date().toISOString()]);
      return jsonResponse({ success: true, message: "Usuário criado com sucesso." });
    }
    
    if (action === "updatePassword") {
      const username = postData.username;
      const newPasswordHash = postData.passwordHash;
      
      const sheet = ss.getSheetByName("users");
      if (!sheet) return jsonResponse({ success: false, error: "Users sheet not initialized." });
      
      const data = sheet.getDataRange().getValues();
      for (let i = 1; i < data.length; i++) {
        if (data[i][0].toLowerCase() === username.toLowerCase()) {
          sheet.getRange(i + 1, 2).setValue(newPasswordHash);
          return jsonResponse({ success: true, message: "Senha atualizada com sucesso." });
        }
      }
      return jsonResponse({ success: false, error: "Usuário não encontrado." });
    }
    
    if (action === "deleteUser") {
      const username = postData.username;
      
      const sheet = ss.getSheetByName("users");
      if (!sheet) return jsonResponse({ success: false, error: "Users sheet not initialized." });
      
      const data = sheet.getDataRange().getValues();
      for (let i = 1; i < data.length; i++) {
        if (data[i][0].toLowerCase() === username.toLowerCase()) {
          sheet.deleteRow(i + 1);
          return jsonResponse({ success: true, message: "Usuário excluído com sucesso." });
        }
      }
      return jsonResponse({ success: false, error: "Usuário não encontrado." });
    }
    
    if (action === "addRecord") {
      const patient = postData.patient;
      const dateLocal = postData.dateLocal;
      const situation = postData.situation;
      const thought = postData.thought;
      const emotion = postData.emotion;
      const behavior = postData.behavior;
      
      const sheet = ss.getSheetByName("records");
      if (!sheet) return jsonResponse({ success: false, error: "Records sheet not initialized." });
      
      const id = "REC_" + Utilities.getUuid();
      const timestamp = new Date().toISOString();
      
      sheet.appendRow([id, patient, dateLocal, situation, thought, emotion, behavior, timestamp]);
      return jsonResponse({ success: true, id: id, message: "Pensamento registrado com sucesso." });
    }
    
    return jsonResponse({ success: false, error: "Action not recognized." }, 400);
    
  } catch (error) {
    return jsonResponse({ success: false, error: error.toString() }, 500);
  }
}
