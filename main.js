const { app, BrowserWindow } = require('electron');
const path = require('path');

let mainWindow;

function createWindow() {
    // Cria a janela com as permissões de segurança liberadas para o Flask
    mainWindow = new BrowserWindow({
        width: 1280,
        height: 800,
        autoHideMenuBar: true,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
            webSecurity: false // Permite que o Electron fale com o servidor Flask local
        }
    });

    // Carrega o arquivo HTML local da tela de login
    mainWindow.loadFile('front/pages/Login.html');

    // Remove a referência quando a janela for fechada
    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

// Quando o Electron estiver pronto, abre a janela
app.whenReady().then(() => {
    createWindow();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) createWindow();
    });
});

// Fecha o processo completamente quando todas as janelas fecharem
app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});