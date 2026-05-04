const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("api", {
  openFolder: () => ipcRenderer.invoke("dialog:openFolder"),
});
