'use strict';

// TAWEE JARVIS — Google Sheets To-Do List Manager
// Source of truth: Google Sheets after OAuth. Local storage is an offline cache/outbox.
(function () {
  'use strict';

  const LS_TASKS = 'tawee_tasks_v1';
  const LS_SHEET_ID = 'tawee_google_tasks_spreadsheet_id_v1';
  const SS_TOKEN = 'tawee_google_access_token_v1';
  const SS_TOKEN_EXP = 'tawee_google_access_token_expiry_v1';
  const FILE_NAME = 'TAWEE AI — Task Manager';
  const SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.file',
  ].join(' ');
  const HEADERS = [
    'Task ID', 'Created At', 'Task', 'Status', 'Priority', 'Deadline',
    'Assignee', 'Category', 'Notes', 'Completed At', 'Updated At',
    'Archived', 'Source', 'Dedupe Key', 'Due Date', 'Due Time',
  ];

  let tokenClient = null;
  let tokenResolver = null;
  let tokenRejecter = null;
  let remoteRows = new Map();
  let addOpen = false;
  let busy = false;
  let lastError = '';

  function esc(value) {
    return String(value ?? '')
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function makeId() {
    if (crypto && typeof crypto.randomUUID === 'function') return crypto.randomUUID();
    return 'tawee-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 10);
  }

  function nowIso() { return new Date().toISOString(); }

  function hashText(text) {
    let h = 2166136261;
    for (let i = 0; i < text.length; i += 1) {
      h ^= text.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    return (h >>> 0).toString(16).padStart(8, '0');
  }

  function dedupeKey(task) {
    return hashText([
      String(task.text || '').trim().toLowerCase().replace(/\s+/g, ' '),
      task.dueDate || '', task.dueTime || '',
      String(task.assignee || '').trim().toLowerCase(),
    ].join('|'));
  }

  function normalizeTask(value) {
    const oldId = value && value.id != null ? String(value.id) : makeId();
    const task = {
      id: /^\d+$/.test(oldId) ? 'legacy-' + oldId : oldId,
      createdAt: value.createdAt ? new Date(value.createdAt).toISOString() : nowIso(),
      text: String(value.text || value.task || '').trim(),
      status: value.status || (value.done ? 'done' : 'pending'),
      priority: value.priority || (value.urgent ? 'urgent' : 'normal'),
      deadline: value.deadline || '',
      assignee: value.assignee || '',
      category: value.category || '',
      notes: value.notes || '',
      completedAt: value.completedAt || (value.done ? nowIso() : ''),
      updatedAt: value.updatedAt || nowIso(),
      archived: value.archived === true || String(value.archived).toUpperCase() === 'TRUE',
      source: value.source || 'tawee',
      dedupeKey: value.dedupeKey || '',
      dueDate: value.dueDate || '',
      dueTime: value.dueTime || '',
      _syncPending: value._syncPending !== false,
    };
    task.dedupeKey = task.dedupeKey || dedupeKey(task);
    return task;
  }

  function getLocalTasks() {
    try {
      const values = JSON.parse(localStorage.getItem(LS_TASKS) || '[]');
      return Array.isArray(values) ? values.map(normalizeTask).filter((x) => x.text) : [];
    } catch (_) { return []; }
  }

  function saveLocalTasks(tasks) {
    try { localStorage.setItem(LS_TASKS, JSON.stringify(tasks)); } catch (_) {}
    renderTasksWidget();
  }

  function tokenValue() {
    const token = sessionStorage.getItem(SS_TOKEN) || '';
    const expiry = Number(sessionStorage.getItem(SS_TOKEN_EXP) || 0);
    if (!token || expiry < Date.now() + 30000) return '';
    return token;
  }

  function clearToken() {
    sessionStorage.removeItem(SS_TOKEN);
    sessionStorage.removeItem(SS_TOKEN_EXP);
    tokenClient = null;
  }

  function spreadsheetId() {
    return (TAWEE.cfg && TAWEE.cfg.googleSpreadsheetId) || localStorage.getItem(LS_SHEET_ID) || '';
  }

  function rememberSpreadsheetId(id) {
    if (!id) return;
    localStorage.setItem(LS_SHEET_ID, id);
    if (TAWEE.cfg) {
      TAWEE.cfg.googleSpreadsheetId = id;
      if (typeof TAWEE.saveCfg === 'function') TAWEE.saveCfg();
    }
  }

  function getClientId() {
    return String((TAWEE.cfg && TAWEE.cfg.googleClientId) || '').trim();
  }

  async function waitForGoogleIdentity() {
    const started = Date.now();
    while (!(window.google && google.accounts && google.accounts.oauth2)) {
      if (Date.now() - started > 10000) {
        throw new Error('โหลด Google Identity Services ไม่สำเร็จ กรุณาตรวจอินเทอร์เน็ตแล้วรีเฟรชหน้า');
      }
      await new Promise((resolve) => setTimeout(resolve, 150));
    }
  }

  async function requestToken() {
    if (location.protocol === 'file:') {
      throw new Error('กรุณาเปิด TAWEE ผ่าน http://localhost หรือ HTTPS — Google OAuth ใช้กับ file:// ไม่ได้');
    }
    const existing = tokenValue();
    if (existing) return existing;
    const clientId = getClientId();
    if (!clientId) throw new Error('ยังไม่ได้ตั้งค่า googleClientId ใน config.json');
    await waitForGoogleIdentity();

    if (!tokenClient) {
      tokenClient = google.accounts.oauth2.initTokenClient({
        client_id: clientId,
        scope: SCOPES,
        include_granted_scopes: true,
        callback: (response) => {
          if (response && response.access_token) {
            sessionStorage.setItem(SS_TOKEN, response.access_token);
            const seconds = Number(response.expires_in || 3600);
            sessionStorage.setItem(SS_TOKEN_EXP, String(Date.now() + seconds * 1000));
            if (tokenResolver) tokenResolver(response.access_token);
          } else if (tokenRejecter) {
            tokenRejecter(new Error((response && response.error_description) || 'Google ไม่ได้คืน access token'));
          }
          tokenResolver = null;
          tokenRejecter = null;
        },
        error_callback: (error) => {
          if (tokenRejecter) tokenRejecter(new Error(error && error.message ? error.message : 'หน้าต่าง Google OAuth ถูกปิด'));
          tokenResolver = null;
          tokenRejecter = null;
        },
      });
    }

    return new Promise((resolve, reject) => {
      tokenResolver = resolve;
      tokenRejecter = reject;
      tokenClient.requestAccessToken({ prompt: 'consent' });
    });
  }

  async function googleApi(url, options) {
    const token = tokenValue();
    if (!token) throw new Error('GOOGLE_AUTH_REQUIRED');
    const init = Object.assign({}, options || {});
    init.headers = Object.assign({}, init.headers || {}, { Authorization: 'Bearer ' + token });
    if (init.body && !init.headers['Content-Type']) init.headers['Content-Type'] = 'application/json';
    const response = await fetch(url, init);
    if (response.status === 401) {
      clearToken();
      throw new Error('GOOGLE_AUTH_EXPIRED');
    }
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      const message = payload && payload.error && payload.error.message ? payload.error.message : 'Google API error ' + response.status;
      throw new Error(message);
    }
    return payload;
  }

  async function findExistingSpreadsheet() {
    const name = encodeURIComponent("name='" + FILE_NAME.replace(/'/g, "\\'") + "' and trashed=false");
    const url = 'https://www.googleapis.com/drive/v3/files?q=' + name +
      '&spaces=drive&orderBy=modifiedTime%20desc&pageSize=10&fields=files(id,name,mimeType,modifiedTime)';
    const data = await googleApi(url);
    const match = (data.files || []).find((f) => f.mimeType === 'application/vnd.google-apps.spreadsheet');
    return match ? match.id : '';
  }

  async function getSpreadsheetMeta(id, includeFormats) {
    const fields = includeFormats
      ? 'spreadsheetId,developerMetadata,sheets(properties(sheetId,title),conditionalFormats)'
      : 'spreadsheetId,developerMetadata,sheets(properties(sheetId,title))';
    return googleApi('https://sheets.googleapis.com/v4/spreadsheets/' + encodeURIComponent(id) + '?fields=' + encodeURIComponent(fields));
  }

  async function createSpreadsheet() {
    const data = await googleApi('https://sheets.googleapis.com/v4/spreadsheets', {
      method: 'POST',
      body: JSON.stringify({
        properties: { title: FILE_NAME, locale: 'th_TH', timeZone: 'Asia/Bangkok' },
        sheets: [
          { properties: { title: 'TASKS', gridProperties: { rowCount: 1000, columnCount: 16 } } },
          { properties: { title: 'DASHBOARD', gridProperties: { rowCount: 50, columnCount: 8 } } },
          { properties: { title: 'LISTS', gridProperties: { rowCount: 100, columnCount: 8 } } },
        ],
      }),
    });
    rememberSpreadsheetId(data.spreadsheetId);
    await setupSpreadsheet(data.spreadsheetId, data);
    return data.spreadsheetId;
  }

  function sheetByTitle(meta, title) {
    return (meta.sheets || []).find((sheet) => sheet.properties && sheet.properties.title === title);
  }

  async function setupSpreadsheet(id, suppliedMeta) {
    let meta = suppliedMeta && suppliedMeta.sheets ? suppliedMeta : await getSpreadsheetMeta(id, true);
    const missing = ['TASKS', 'DASHBOARD', 'LISTS'].filter((name) => !sheetByTitle(meta, name));
    if (missing.length) {
      await googleApi('https://sheets.googleapis.com/v4/spreadsheets/' + encodeURIComponent(id) + ':batchUpdate', {
        method: 'POST',
        body: JSON.stringify({ requests: missing.map((title) => ({ addSheet: { properties: { title } } })) }),
      });
      meta = await getSpreadsheetMeta(id, true);
    }

    const tasksSheet = sheetByTitle(meta, 'TASKS');
    const dashboardSheet = sheetByTitle(meta, 'DASHBOARD');
    const listsSheet = sheetByTitle(meta, 'LISTS');
    const taskId = tasksSheet.properties.sheetId;
    const dashboardId = dashboardSheet.properties.sheetId;
    const listsId = listsSheet.properties.sheetId;

    const dashboard = [
      ['TAWEE AI — TASK DASHBOARD', 'ค่า'],
      ['งานเปิดอยู่', '=COUNTIFS(TASKS!D2:D,"<>done",TASKS!L2:L,FALSE,TASKS!A2:A,"<>")'],
      ['เลยกำหนด', '=COUNTIFS(TASKS!O2:O,"<"&TODAY(),TASKS!O2:O,"<>",TASKS!D2:D,"<>done",TASKS!L2:L,FALSE)'],
      ['ครบกำหนดวันนี้', '=COUNTIFS(TASKS!O2:O,TODAY(),TASKS!D2:D,"<>done",TASKS!L2:L,FALSE)'],
      ['เสร็จแล้ว', '=COUNTIF(TASKS!D2:D,"done")'],
      ['Completion Rate', '=IFERROR(COUNTIF(TASKS!D2:D,"done")/COUNTIF(TASKS!A2:A,"<>"),0)'],
      ['On-time Rate', '=IFERROR(SUMPRODUCT((TASKS!D2:D10000="done")*(TASKS!O2:O10000<>"")*(INT(TASKS!J2:J10000)<=TASKS!O2:O10000))/COUNTIF(TASKS!D2:D10000,"done"),0)'],
      ['อัปเดตล่าสุด', nowIso()],
    ];
    const lists = [
      ['Status', 'Priority', 'Archived'],
      ['pending', 'low', 'FALSE'],
      ['in_progress', 'normal', 'TRUE'],
      ['done', 'high', ''],
      ['', 'urgent', ''],
    ];

    await googleApi('https://sheets.googleapis.com/v4/spreadsheets/' + encodeURIComponent(id) + '/values:batchUpdate', {
      method: 'POST',
      body: JSON.stringify({
        valueInputOption: 'USER_ENTERED',
        data: [
          { range: 'TASKS!A1:P1', values: [HEADERS] },
          { range: 'DASHBOARD!A1:B8', values: dashboard },
          { range: 'LISTS!A1:C5', values: lists },
        ],
      }),
    });

    const requests = [];
    const existingRules = tasksSheet.conditionalFormats || [];
    for (let i = existingRules.length - 1; i >= 0; i -= 1) {
      requests.push({ deleteConditionalFormatRule: { sheetId: taskId, index: i } });
    }
    requests.push(
      { updateSheetProperties: { properties: { sheetId: taskId, gridProperties: { frozenRowCount: 1 } }, fields: 'gridProperties.frozenRowCount' } },
      { updateSheetProperties: { properties: { sheetId: dashboardId, gridProperties: { frozenRowCount: 1 } }, fields: 'gridProperties.frozenRowCount' } },
      { updateSheetProperties: { properties: { sheetId: listsId, hidden: true }, fields: 'hidden' } },
      { setBasicFilter: { filter: { range: { sheetId: taskId, startRowIndex: 0, startColumnIndex: 0, endColumnIndex: 16 } } } },
      { repeatCell: { range: { sheetId: taskId, startRowIndex: 0, endRowIndex: 1, startColumnIndex: 0, endColumnIndex: 16 }, cell: { userEnteredFormat: { backgroundColor: { red: 0.04, green: 0.24, blue: 0.18 }, textFormat: { foregroundColor: { red: 1, green: 1, blue: 1 }, bold: true }, horizontalAlignment: 'CENTER' } }, fields: 'userEnteredFormat' } },
      { repeatCell: { range: { sheetId: dashboardId, startRowIndex: 0, endRowIndex: 1, startColumnIndex: 0, endColumnIndex: 2 }, cell: { userEnteredFormat: { backgroundColor: { red: 0.08, green: 0.36, blue: 0.26 }, textFormat: { foregroundColor: { red: 1, green: 1, blue: 1 }, bold: true, fontSize: 13 } } }, fields: 'userEnteredFormat' } },
      { repeatCell: { range: { sheetId: dashboardId, startRowIndex: 1, endRowIndex: 8, startColumnIndex: 0, endColumnIndex: 2 }, cell: { userEnteredFormat: { backgroundColor: { red: 0.94, green: 0.98, blue: 0.96 } } }, fields: 'userEnteredFormat.backgroundColor' } },
      { repeatCell: { range: { sheetId: dashboardId, startRowIndex: 5, endRowIndex: 7, startColumnIndex: 1, endColumnIndex: 2 }, cell: { userEnteredFormat: { numberFormat: { type: 'PERCENT', pattern: '0.0%' } } }, fields: 'userEnteredFormat.numberFormat' } },
      { repeatCell: { range: { sheetId: taskId, startRowIndex: 1, startColumnIndex: 14, endColumnIndex: 15 }, cell: { userEnteredFormat: { numberFormat: { type: 'DATE', pattern: 'yyyy-mm-dd' } } }, fields: 'userEnteredFormat.numberFormat' } },
      { setDataValidation: { range: { sheetId: taskId, startRowIndex: 1, startColumnIndex: 3, endColumnIndex: 4 }, rule: { condition: { type: 'ONE_OF_LIST', values: [{ userEnteredValue: 'pending' }, { userEnteredValue: 'in_progress' }, { userEnteredValue: 'done' }] }, strict: true, showCustomUi: true } } },
      { setDataValidation: { range: { sheetId: taskId, startRowIndex: 1, startColumnIndex: 4, endColumnIndex: 5 }, rule: { condition: { type: 'ONE_OF_LIST', values: [{ userEnteredValue: 'low' }, { userEnteredValue: 'normal' }, { userEnteredValue: 'high' }, { userEnteredValue: 'urgent' }] }, strict: true, showCustomUi: true } } },
      { setDataValidation: { range: { sheetId: taskId, startRowIndex: 1, startColumnIndex: 11, endColumnIndex: 12 }, rule: { condition: { type: 'ONE_OF_LIST', values: [{ userEnteredValue: 'FALSE' }, { userEnteredValue: 'TRUE' }] }, strict: true, showCustomUi: true } } },
      { updateDimensionProperties: { range: { sheetId: taskId, dimension: 'COLUMNS', startIndex: 2, endIndex: 3 }, properties: { pixelSize: 320 }, fields: 'pixelSize' } },
      { updateDimensionProperties: { range: { sheetId: taskId, dimension: 'COLUMNS', startIndex: 0, endIndex: 2 }, properties: { pixelSize: 165 }, fields: 'pixelSize' } },
      { updateDimensionProperties: { range: { sheetId: taskId, dimension: 'COLUMNS', startIndex: 3, endIndex: 16 }, properties: { pixelSize: 125 }, fields: 'pixelSize' } },
      { updateDimensionProperties: { range: { sheetId: dashboardId, dimension: 'COLUMNS', startIndex: 0, endIndex: 1 }, properties: { pixelSize: 220 }, fields: 'pixelSize' } },
      { updateDimensionProperties: { range: { sheetId: dashboardId, dimension: 'COLUMNS', startIndex: 1, endIndex: 2 }, properties: { pixelSize: 150 }, fields: 'pixelSize' } },
      conditionalRule(taskId, '=$D2="done"', { red: 0.82, green: 0.95, blue: 0.86 }),
      conditionalRule(taskId, '=AND($D2<>"done",$O2<TODAY(),$O2<>"",$L2=FALSE)', { red: 1, green: 0.82, blue: 0.82 }),
      conditionalRule(taskId, '=AND($D2<>"done",$O2=TODAY(),$L2=FALSE)', { red: 1, green: 0.94, blue: 0.68 }),
      conditionalRule(taskId, '=$E2="urgent"', { red: 1, green: 0.78, blue: 0.88 }),
    );

    const markerExists = (meta.developerMetadata || []).some((m) => m.metadataKey === 'tawee_task_manager_schema');
    if (!markerExists) {
      requests.push({ createDeveloperMetadata: { developerMetadata: { metadataKey: 'tawee_task_manager_schema', metadataValue: 'v1', visibility: 'DOCUMENT', location: { spreadsheet: true } } } });
    }

    await googleApi('https://sheets.googleapis.com/v4/spreadsheets/' + encodeURIComponent(id) + ':batchUpdate', {
      method: 'POST', body: JSON.stringify({ requests }),
    });
  }

  function conditionalRule(sheetId, formula, color) {
    return {
      addConditionalFormatRule: {
        index: 0,
        rule: {
          ranges: [{ sheetId, startRowIndex: 1, startColumnIndex: 0, endColumnIndex: 16 }],
          booleanRule: { condition: { type: 'CUSTOM_FORMULA', values: [{ userEnteredValue: formula }] }, format: { backgroundColor: color } },
        },
      },
    };
  }

  async function ensureSpreadsheet() {
    let id = spreadsheetId();
    if (id) {
      try {
        await getSpreadsheetMeta(id, false);
        rememberSpreadsheetId(id);
        return id;
      } catch (_) {
        localStorage.removeItem(LS_SHEET_ID);
        id = '';
      }
    }
    id = await findExistingSpreadsheet();
    if (id) {
      rememberSpreadsheetId(id);
      await setupSpreadsheet(id);
      return id;
    }
    return createSpreadsheet();
  }

  function taskToRow(task) {
    return [[
      task.id, task.createdAt, task.text, task.status, task.priority, task.deadline,
      task.assignee, task.category, task.notes, task.completedAt, task.updatedAt,
      task.archived ? 'TRUE' : 'FALSE', task.source, task.dedupeKey,
      task.dueDate, task.dueTime,
    ]];
  }

  function rowToTask(row, rowNumber) {
    const task = normalizeTask({
      id: row[0], createdAt: row[1], text: row[2], status: row[3], priority: row[4],
      deadline: row[5], assignee: row[6], category: row[7], notes: row[8],
      completedAt: row[9], updatedAt: row[10], archived: row[11], source: row[12],
      dedupeKey: row[13], dueDate: row[14], dueTime: row[15], _syncPending: false,
    });
    task._rowNumber = rowNumber;
    return task;
  }

  async function loadRemoteTasks() {
    const id = await ensureSpreadsheet();
    const data = await googleApi('https://sheets.googleapis.com/v4/spreadsheets/' + encodeURIComponent(id) + '/values/' + encodeURIComponent('TASKS!A2:P10000'));
    const tasks = (data.values || []).map((row, index) => rowToTask(row, index + 2)).filter((x) => x.id && x.text);
    remoteRows = new Map(tasks.map((task) => [task.id, task._rowNumber]));
    return tasks;
  }

  async function writeTask(task) {
    const id = await ensureSpreadsheet();
    const rowNumber = remoteRows.get(task.id);
    const base = 'https://sheets.googleapis.com/v4/spreadsheets/' + encodeURIComponent(id) + '/values/';
    if (rowNumber) {
      await googleApi(base + encodeURIComponent('TASKS!A' + rowNumber + ':P' + rowNumber) + '?valueInputOption=USER_ENTERED', {
        method: 'PUT', body: JSON.stringify({ values: taskToRow(task) }),
      });
    } else {
      const response = await googleApi(base + encodeURIComponent('TASKS!A:P') + ':append?valueInputOption=USER_ENTERED&insertDataOption=INSERT_ROWS', {
        method: 'POST', body: JSON.stringify({ values: taskToRow(task) }),
      });
      const range = response.updates && response.updates.updatedRange;
      const match = range && range.match(/![A-Z]+(\d+):/);
      if (match) remoteRows.set(task.id, Number(match[1]));
    }
    task._syncPending = false;
    return task;
  }

  async function syncAll() {
    const local = getLocalTasks();
    const remote = await loadRemoteTasks();
    const byId = new Map(remote.map((task) => [task.id, task]));
    for (const task of local) {
      if (task._syncPending || !byId.has(task.id)) {
        await writeTask(task);
        byId.set(task.id, task);
      }
    }
    const merged = Array.from(byId.values()).sort((a, b) => String(a.createdAt).localeCompare(String(b.createdAt)));
    saveLocalTasks(merged);
    return merged;
  }

  async function connect() {
    if (busy) return;
    busy = true;
    lastError = '';
    renderTasksWidget();
    try {
      await requestToken();
      await ensureSpreadsheet();
      const tasks = await syncAll();
      notify('เชื่อมต่อ Google Sheets สำเร็จ ซิงก์แล้ว ' + tasks.length + ' งาน');
    } catch (error) {
      lastError = friendlyError(error);
      notify('เชื่อมต่อ Google ไม่สำเร็จ: ' + lastError, true);
    } finally {
      busy = false;
      renderTasksWidget();
    }
  }

  function disconnect() {
    clearToken();
    lastError = '';
    renderTasksWidget();
    notify('ตัดการเชื่อมต่อ Google ในแท็บนี้แล้ว');
  }

  function friendlyError(error) {
    const message = String(error && error.message ? error.message : error || 'ไม่ทราบสาเหตุ');
    if (message.includes('GOOGLE_AUTH_EXPIRED')) return 'สิทธิ์หมดอายุ กรุณากดเชื่อมต่อ Google ใหม่';
    if (message.includes('GOOGLE_AUTH_REQUIRED')) return 'กรุณากดเชื่อมต่อ Google';
    if (/popup|closed|cancel/i.test(message)) return 'หน้าต่างล็อกอินถูกปิดหรือเบราว์เซอร์บล็อก popup';
    return message;
  }

  function notify(message, isError) {
    if (typeof TAWEE.pushMsg === 'function') TAWEE.pushMsg(isError ? 'system' : 'assistant', message);
    if (typeof TAWEE.render === 'function') TAWEE.render();
  }

  function parseThaiTime(text) {
    const lower = text.toLowerCase();
    const date = new Date();
    let hasDate = false;
    if (/มะรืน/.test(lower)) { date.setDate(date.getDate() + 2); hasDate = true; }
    else if (/พรุ่งนี้/.test(lower)) { date.setDate(date.getDate() + 1); hasDate = true; }
    else if (/วันนี้/.test(lower)) { hasDate = true; }
    const iso = lower.match(/\b(20\d{2})-(\d{1,2})-(\d{1,2})\b/);
    if (iso) {
      date.setFullYear(Number(iso[1]), Number(iso[2]) - 1, Number(iso[3]));
      hasDate = true;
    }
    let dueTime = '';
    const colon = lower.match(/\b([01]?\d|2[0-3])[:.]([0-5]\d)\b/);
    const clock = lower.match(/\b([01]?\d|2[0-3])\s*นาฬิกา\b/);
    if (colon) dueTime = String(Number(colon[1])).padStart(2, '0') + ':' + colon[2];
    else if (clock) dueTime = String(Number(clock[1])).padStart(2, '0') + ':00';
    const dueDate = hasDate
      ? [date.getFullYear(), String(date.getMonth() + 1).padStart(2, '0'), String(date.getDate()).padStart(2, '0')].join('-')
      : '';
    return { dueDate, dueTime };
  }

  function extractTaskText(raw) {
    let text = raw.trim();
    text = text.replace(/^(?:เพิ่มงาน(?:ด่วน)?|จดงาน|ช่วยเตือน(?:ฉัน)?|เตือน(?:ฉัน)?(?:ว่า)?|สร้างงาน)\s*/i, '');
    text = text.replace(/(?:วันนี้|พรุ่งนี้|มะรืน)/gi, '');
    text = text.replace(/20\d{2}-\d{1,2}-\d{1,2}/g, '');
    text = text.replace(/(?:[01]?\d|2[0-3])[:.]\d{2}/g, '');
    text = text.replace(/(?:[01]?\d|2[0-3])\s*นาฬิกา/g, '');
    text = text.replace(/(?:เวลา|ตอน)\s*$/i, '');
    text = text.replace(/^(?:ต้อง|อย่าลืม|ให้)\s*/i, '');
    text = text.replace(/\s+/g, ' ').trim();
    return text;
  }

  function parseTask(raw) {
    const time = parseThaiTime(raw);
    const assigneeMatch = raw.match(/(?:ผู้รับผิดชอบ|มอบให้)\s*([^,，]+?)(?:\s+(?:ภายใน|ก่อน|วันที่|วันนี้|พรุ่งนี้|มะรืน)|$)/i);
    const categoryMatch = raw.match(/(?:หมวด|ประเภท)\s*([^,，]+?)(?:\s+(?:ภายใน|ก่อน|วันที่|วันนี้|พรุ่งนี้|มะรืน)|$)/i);
    const task = normalizeTask({
      id: makeId(), text: extractTaskText(raw), status: 'pending',
      priority: /ด่วนมาก|urgent/i.test(raw) ? 'urgent' : /ด่วน|สำคัญมาก/i.test(raw) ? 'high' : 'normal',
      deadline: [time.dueDate, time.dueTime].filter(Boolean).join(' '),
      assignee: assigneeMatch ? assigneeMatch[1].trim() : '',
      category: categoryMatch ? categoryMatch[1].trim() : '',
      dueDate: time.dueDate, dueTime: time.dueTime, source: 'tawee', _syncPending: true,
    });
    task.dedupeKey = dedupeKey(task);
    return task;
  }

  function visibleTasks(tasks) {
    return tasks.filter((task) => !task.archived);
  }

  function findTask(tasks, query) {
    const key = String(query || '').trim().toLowerCase();
    if (!key || /^(?:นี้|งานนี้)$/.test(key)) return null;
    return visibleTasks(tasks).find((task) => task.id.toLowerCase().startsWith(key) || task.text.toLowerCase().includes(key));
  }

  async function persistTask(task, tasks) {
    task.updatedAt = nowIso();
    task._syncPending = true;
    saveLocalTasks(tasks);
    if (!tokenValue()) return false;
    try {
      await writeTask(task);
      saveLocalTasks(tasks);
      return true;
    } catch (error) {
      lastError = friendlyError(error);
      saveLocalTasks(tasks);
      return false;
    }
  }

  function formatTask(task, index) {
    const flag = task.priority === 'urgent' ? 'ด่วนมาก — ' : task.priority === 'high' ? 'ด่วน — ' : '';
    const due = task.deadline ? ' (กำหนด ' + task.deadline + ')' : '';
    return (index + 1) + '. ' + flag + task.text + due + (task.assignee ? ' — ' + task.assignee : '');
  }

  function isConnected() { return !!tokenValue(); }

  const LIST_RE = /(?:มีอะไรค้าง|งานค้าง|งานของฉัน|ดูงาน|รายการงาน|งานที่ต้องทำ)(?:วันนี้)?/i;
  const DONE_RE = /^(?:งานนี้เสร็จแล้ว|เสร็จงาน|งานเสร็จแล้ว|ทำเสร็จแล้ว|ปิดงาน)\s*(.*)$/i;
  const DELETE_RE = /^(?:ลบงาน|เก็บงาน|archive)\s+(.+)/i;
  const CONFIRM_DELETE_RE = /^ยืนยัน(?:ลบ|เก็บงาน)\s+(.+)/i;
  const UPDATE_RE = /^(?:แก้งาน|อัปเดตงาน|เปลี่ยนงาน)\s+(.+)/i;
  const CREATE_RE = /^(?:เพิ่มงาน|จดงาน|สร้างงาน|ช่วยเตือน|เตือนฉัน)|(?:วันนี้|พรุ่งนี้|มะรืน).*(?:ต้อง|โทร|ส่ง|ทำ|ซื้อ|จ่าย|นัด)|\bต้อง\s+.+/i;
  const MATCH_RE = new RegExp([LIST_RE, DONE_RE, DELETE_RE, CONFIRM_DELETE_RE, UPDATE_RE, CREATE_RE].map((r) => r.source).join('|'), 'i');

  async function handleCommand(_lower, raw) {
    let tasks = getLocalTasks();

    const confirmDelete = raw.match(CONFIRM_DELETE_RE);
    if (confirmDelete) {
      const task = findTask(tasks, confirmDelete[1]);
      if (!task) return 'ไม่พบงานที่ต้องการเก็บ กรุณาระบุชื่อหรือรหัสงานให้ชัดเจน';
      task.archived = true;
      const synced = await persistTask(task, tasks);
      return 'เก็บงาน "' + task.text + '" แล้ว' + (synced ? ' และซิงก์ Google Sheets สำเร็จ' : ' โดยเก็บไว้รอซิงก์');
    }

    const deletion = raw.match(DELETE_RE);
    if (deletion) {
      const task = findTask(tasks, deletion[1]);
      if (!task) return 'ไม่พบงาน "' + deletion[1].trim() + '" กรุณาระบุชื่อหรือรหัสงานให้ชัดเจน';
      return 'พบงาน "' + task.text + '" — เพื่อป้องกันการลบผิด ให้พิมพ์ “ยืนยันลบ ' + task.id.slice(0, 8) + '” ข้อมูลจะถูกเก็บถาวรแบบกู้คืนได้ ไม่ลบแถวทิ้ง';
    }

    const done = raw.match(DONE_RE);
    if (done) {
      if (!done[1] || /^(?:นี้|งานนี้)$/.test(done[1].trim())) return 'กรุณาบอกชื่องานที่จะทำเครื่องหมายว่าเสร็จ เช่น “งานเสร็จแล้ว โทรหาลูกค้า A”';
      const task = findTask(tasks, done[1]);
      if (!task) return 'ไม่พบงาน "' + done[1].trim() + '" ในรายการ';
      task.status = 'done';
      task.completedAt = nowIso();
      const synced = await persistTask(task, tasks);
      return 'ทำเครื่องหมายว่าเสร็จแล้ว: "' + task.text + '"' + (synced ? ' และซิงก์ Google Sheets สำเร็จ' : ' โดยเก็บไว้รอซิงก์');
    }

    const update = raw.match(UPDATE_RE);
    if (update) {
      return 'กรุณาระบุรูปแบบให้ชัดเจน เช่น “งานเสร็จแล้ว ชื่องาน” หรือเพิ่มงานใหม่พร้อมกำหนดเวลา ระบบจะไม่เดาการแก้ไขที่อาจเปลี่ยนงานผิดรายการ';
    }

    if (LIST_RE.test(raw)) {
      if (isConnected()) {
        try { tasks = await syncAll(); } catch (error) { lastError = friendlyError(error); }
      }
      let pending = visibleTasks(tasks).filter((task) => task.status !== 'done');
      if (/วันนี้/.test(raw)) {
        const today = new Date();
        const dateKey = [today.getFullYear(), String(today.getMonth() + 1).padStart(2, '0'), String(today.getDate()).padStart(2, '0')].join('-');
        pending = pending.filter((task) => !task.dueDate || task.dueDate === dateKey);
      }
      pending.sort((a, b) => priorityWeight(b.priority) - priorityWeight(a.priority) || String(a.dueDate).localeCompare(String(b.dueDate)));
      if (!pending.length) return 'ไม่มีงานค้างตามเงื่อนไขนี้';
      return 'งานค้าง ' + pending.length + ' รายการ:\n' + pending.map(formatTask).join('\n') + (isConnected() ? '' : '\n\nกำลังใช้ข้อมูลในเครื่อง กด “เชื่อมต่อ Google” ในแผงงานเพื่อซิงก์');
    }

    if (CREATE_RE.test(raw)) {
      const task = parseTask(raw);
      if (!task.text) return 'กรุณาบอกชื่องาน เช่น “พรุ่งนี้ต้องโทรหาลูกค้า A เวลา 10:00”';
      const duplicate = visibleTasks(tasks).find((item) => item.status !== 'done' && item.dedupeKey === task.dedupeKey);
      if (duplicate) return 'งานนี้มีอยู่แล้ว จึงไม่สร้างซ้ำ: "' + duplicate.text + '"';
      tasks.push(task);
      const synced = await persistTask(task, tasks);
      return 'เพิ่มงานแล้ว: "' + task.text + '"' + (task.deadline ? ' กำหนด ' + task.deadline : '') +
        (synced ? ' และบันทึกลง Google Sheets สำเร็จ' : ' — บันทึกในเครื่องและรอซิงก์ Google');
    }

    return null;
  }

  function priorityWeight(priority) {
    return ({ urgent: 4, high: 3, normal: 2, low: 1 })[priority] || 0;
  }

  function injectStyles() {
    if (document.getElementById('tawee-tasks-style')) return;
    const style = document.createElement('style');
    style.id = 'tawee-tasks-style';
    style.textContent = `
      .tawee-task-panel{display:flex;flex-direction:column;gap:8px;min-width:230px;max-width:290px;padding:10px;border-radius:16px;background:rgba(6,12,12,.88);border:1px solid rgba(var(--accentRGB),.35);backdrop-filter:blur(16px);box-shadow:0 10px 30px rgba(0,0,0,.4)}
      .tawee-task-toolbar{display:flex;align-items:center;gap:7px;justify-content:space-between}
      .tawee-task-status{font-size:10px;color:rgba(255,255,255,.55);font-family:'JetBrains Mono',monospace}
      .tawee-task-button{border:1px solid rgba(var(--accentRGB),.5);background:rgba(var(--accentRGB),.13);color:var(--accent);border-radius:9px;padding:6px 9px;font-size:10.5px;cursor:pointer}
      .tawee-task-button:disabled{opacity:.5;cursor:wait}
      .tawee-task-row{display:flex;gap:8px;align-items:center;padding:7px;border-radius:11px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08)}
      .tawee-task-row.urgent{border-color:rgba(255,90,140,.55)}
      .tawee-task-title{font-size:11.5px;color:#fff;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;flex:1}
      .tawee-task-meta{font-size:9.5px;color:rgba(255,255,255,.42)}
      .tawee-task-icon{width:24px;height:24px;border-radius:50%;border:1px solid rgba(255,255,255,.25);background:transparent;color:var(--accent);cursor:pointer}
      .tawee-task-addbox{display:flex;gap:6px}
      .tawee-task-addbox input{min-width:0;flex:1;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.15);border-radius:9px;color:#fff;padding:7px}
    `;
    document.head.appendChild(style);
  }

  function renderInto(container) {
    if (!container) return;
    injectStyles();
    const tasks = visibleTasks(getLocalTasks()).filter((task) => task.status !== 'done')
      .sort((a, b) => priorityWeight(b.priority) - priorityWeight(a.priority) || String(a.createdAt).localeCompare(String(b.createdAt)));
    const connected = isConnected();
    const statusText = busy ? 'กำลังเชื่อมต่อ…' : connected ? 'Google เชื่อมต่อแล้ว' : 'ยังไม่เชื่อม Google';
    const connectButton = connected
      ? '<button class="tawee-task-button" onclick="TAWEE.tasks.disconnect()">ตัดการเชื่อมต่อ</button>'
      : '<button class="tawee-task-button" onclick="TAWEE.tasks.connect()"' + (busy ? ' disabled' : '') + '>เชื่อมต่อ Google</button>';
    const openSheet = spreadsheetId()
      ? '<a class="tawee-task-button" style="text-decoration:none" target="_blank" rel="noopener" href="https://docs.google.com/spreadsheets/d/' + encodeURIComponent(spreadsheetId()) + '/edit">เปิดชีต</a>'
      : '';
    const rows = tasks.slice(0, 8).map((task) =>
      '<div class="tawee-task-row' + (task.priority === 'urgent' ? ' urgent' : '') + '">' +
        '<button class="tawee-task-icon" title="เสร็จแล้ว" onclick="TAWEE.tasks.complete(\'' + esc(task.id) + '\')">✓</button>' +
        '<div style="min-width:0;flex:1"><div class="tawee-task-title">' + esc(task.text) + '</div>' +
        '<div class="tawee-task-meta">' + esc(task.deadline || task.priority) + '</div></div>' +
        '<button class="tawee-task-icon" title="เก็บงาน" onclick="TAWEE.tasks.archive(\'' + esc(task.id) + '\')">×</button>' +
      '</div>'
    ).join('');
    const addBox = addOpen
      ? '<div class="tawee-task-addbox"><input id="tawee-task-add-input" placeholder="ชื่องานใหม่" onkeydown="if(event.key===\'Enter\')TAWEE.tasks.submitAdd();if(event.key===\'Escape\')TAWEE.tasks.closeAdd()"><button class="tawee-task-button" onclick="TAWEE.tasks.submitAdd()">เพิ่ม</button></div>'
      : '<button class="tawee-task-button" onclick="TAWEE.tasks.openAdd()">+ เพิ่มงาน</button>';
    container.innerHTML = '<div class="tawee-task-panel">' +
      '<div class="tawee-task-toolbar"><span class="tawee-task-status">' + esc(statusText) + '</span><span style="display:flex;gap:5px">' + openSheet + connectButton + '</span></div>' +
      (lastError ? '<div style="font-size:10px;color:#ff9bab">' + esc(lastError) + '</div>' : '') +
      addBox + (rows || '<div class="tawee-task-meta">ยังไม่มีงานค้าง</div>') +
      (tasks.length > 8 ? '<div class="tawee-task-meta">และอีก ' + (tasks.length - 8) + ' งาน</div>' : '') +
      '</div>';
    if (addOpen) {
      const input = document.getElementById('tawee-task-add-input');
      if (input) input.focus();
    }
  }

  function renderTasksWidget() {
    if (typeof TAWEE !== 'undefined' && TAWEE.hub && typeof TAWEE.hub.refresh === 'function') TAWEE.hub.refresh();
  }

  async function completeById(id) {
    const tasks = getLocalTasks();
    const task = tasks.find((item) => item.id === id);
    if (!task) return;
    task.status = 'done';
    task.completedAt = nowIso();
    await persistTask(task, tasks);
  }

  async function archiveById(id) {
    const tasks = getLocalTasks();
    const task = tasks.find((item) => item.id === id);
    if (!task) return;
    task.archived = true;
    await persistTask(task, tasks);
  }

  async function submitAdd() {
    const input = document.getElementById('tawee-task-add-input');
    const value = input ? input.value.trim() : '';
    addOpen = false;
    if (!value) { renderTasksWidget(); return; }
    const tasks = getLocalTasks();
    const task = parseTask('เพิ่มงาน ' + value);
    if (visibleTasks(tasks).some((item) => item.status !== 'done' && item.dedupeKey === task.dedupeKey)) {
      notify('งานนี้มีอยู่แล้ว จึงไม่สร้างซ้ำ');
      renderTasksWidget();
      return;
    }
    tasks.push(task);
    await persistTask(task, tasks);
  }

  TAWEE.registerSkill('tasks', {
    match: (text) => MATCH_RE.test(text),
    handle: handleCommand,
  });

  TAWEE.tasks = {
    connect,
    disconnect,
    sync: syncAll,
    complete: completeById,
    archive: archiveById,
    remove: archiveById,
    add(text) { return submitDirect(text); },
    getAll: getLocalTasks,
    openAdd() { addOpen = true; renderTasksWidget(); },
    closeAdd() { addOpen = false; renderTasksWidget(); },
    submitAdd,
    renderInto,
    spreadsheetId,
  };

  async function submitDirect(text) {
    const tasks = getLocalTasks();
    const task = parseTask('เพิ่มงาน ' + text);
    if (!task.text) return null;
    if (visibleTasks(tasks).some((item) => item.status !== 'done' && item.dedupeKey === task.dedupeKey)) return null;
    tasks.push(task);
    await persistTask(task, tasks);
    return task;
  }

  injectStyles();
})();
