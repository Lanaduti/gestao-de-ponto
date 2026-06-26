const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

let mainWindow;
let pythonProcess;

function startPythonServer() {
    const isPackaged = app.isPackaged;
    
    let pythonExecutable;
    let args = [];
    let cwd = __dirname;
    
    if (isPackaged) {
        // No build, o server.exe estará na pasta resources/server/
        pythonExecutable = path.join(process.resourcesPath, 'server', 'server.exe');
        cwd = process.resourcesPath;
    } else {
        // Em dev, usa o pyinstaller dist se existir, senão python puro
        const exePath = path.join(__dirname, 'dist', 'server', 'server.exe');
        if (fs.existsSync(exePath)) {
            pythonExecutable = exePath;
        } else {
            pythonExecutable = 'python';
            args = ['server.py'];
        }
    }

    console.log('Iniciando backend:', pythonExecutable, args);
    
    pythonProcess = spawn(pythonExecutable, args, { cwd: cwd });

    pythonProcess.stdout.on('data', (data) => {
        console.log(`Flask: ${data}`);
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`Flask Error: ${data}`);
    });
}

function loadWithRetry(window, url, retries = 10, delay = 1000) {
    window.loadURL(url).catch(() => {
        if (retries > 0) {
            setTimeout(() => loadWithRetry(window, url, retries - 1, delay), delay);
        }
    });
}

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1280,
        height: 800,
        autoHideMenuBar: true,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
            webSecurity: false 
        }
    });

    // Carrega o servidor Flask com tentativas de reconexão
    loadWithRetry(mainWindow, 'http://localhost:5000');

    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

app.whenReady().then(() => {
    startPythonServer();
    
    // Aguarda o Flask iniciar antes de carregar a janela
    setTimeout(() => {
        createWindow();
    }, 5000);

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) createWindow();
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('will-quit', () => {
    if (pythonProcess) {
        pythonProcess.kill();
    }
});