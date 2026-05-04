const { app, BrowserWindow, ipcMain, dialog, Menu } = require("electron");
const path = require("path");

const isDev = true;

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
    },
  });

  if (isDev) {
    win.loadURL("http://localhost:5173");
    win.webContents.openDevTools();
  } else {
    win.loadFile(path.join(__dirname, "../frontend/index.html"));
  }

  const template = [
    {
      label: "File",
      submenu: [
        {
          label: "Open Folder",
          click: async () => {
            // we’ll connect this to your existing API
          },
        },
        { type: "separator" },
        {
          label: "Exit",
          role: "quit",
        },
      ],
    },
  ];
  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

ipcMain.handle("dialog:openFolder", async () => {
  const result = await dialog.showOpenDialog({
    properties: ["openDirectory"],
  });

  if (result.canceled) return null;

  return result.filePaths[0];
});

app.whenReady().then(() => {
  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on("window-all-closed", () => {
  // if (process.platform !== "darwin") {
  //   app.quit();
  // }
  app.quit();
});
