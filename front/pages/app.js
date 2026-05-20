/**
 * app.js - Administrador Central do Sistema
 * Gerencia rotas, sessões e permissões de acesso.
 */

const HCP_App = {
    // Configurações globais
    config: {
        adminEmail: 'admin@empresa.com',
        loginPage: 'Login.html',
        dashboardPage: 'Dashboard.html',
        funcionariosPage: 'funcionarios.html',
        relatorioAdminPage: 'relatorio-admin.html',
        baterPontoPage: 'baterPonto.html',
        relatorioPage: 'relatorio.html',
        homePage: 'home.html',
        justificativaPage: 'justificativa.html',
        contrachequePage: 'contracheque.html'
    },

    /**
     * Executa o login salvando a sessão e redirecionando pelo cargo
     */
    async login(email, password) {
        if (!email || !password) return alert('Por favor, preencha todos os campos');
        
        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                localStorage.setItem('loggedUser', JSON.stringify({ 
                    ...data,
                    loginTime: new Date().getTime()
                }));
                this.redirect(data.email);
            } else {
                alert(data.mensagem || 'Erro ao realizar login');
            }
        } catch (error) {
            alert('Erro ao conectar com o servidor. Verifique se o server.py está rodando.');
        }
    },

    /**
     * Envia os dados de um novo funcionário para o servidor
     */
    async cadastrar(data) {
        if (data.password !== data.confirm_password) return alert('As senhas não conferem');
        
        try {
            const response = await fetch('/api/admin/cadastrar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            if (response.ok) {
                alert('Funcionário cadastrado com sucesso!');
                window.location.href = this.config.funcionariosPage;
            } else {
                alert(result.mensagem || 'Erro ao realizar cadastro');
            }
        } catch (error) {
            alert('Erro ao conectar com o servidor.');
        }
    },

    /**
     * Encerra a sessão e limpa os dados do navegador
     */
    logout() {
        localStorage.removeItem('loggedUser');
        const isInPagesFolder = window.location.pathname.includes('/pages/');
        const destination = isInPagesFolder ? this.config.loginPage : 'pages/' + this.config.loginPage;
        window.location.href = destination;
    },

    /**
     * Lógica de redirecionamento: Lana vai para Dashboard, outros para Home
     */
    redirect(email) {
        const isAdmin = email.toLowerCase() === this.config.adminEmail;
        let destination = isAdmin 
            ? this.config.dashboardPage 
            : this.config.homePage;
        
        const isAtRoot = !window.location.pathname.includes('/pages/');
        if (isAtRoot) destination = 'pages/' + destination;
        
        window.location.href = destination;
    },

    /**
     * Verifica se o usuário está logado. Se não, manda para o login.
     */
    checkAuth() {
        if (window.location.pathname.includes(this.config.loginPage)) return null;
        
        const user = JSON.parse(localStorage.getItem('loggedUser'));
        if (!user) {
            this.logout();
            return null;
        }
        // Garante que id_funcionario esteja presente para usuários que não são admin
        if (!user.id_funcionario && user.email !== this.config.adminEmail) {
            console.error("Erro: Usuário logado não possui id_funcionario. Verifique o processo de login/cadastro.");
            // Opcionalmente, você pode querer deslogar ou redirecionar aqui se for um erro crítico
        }
        return user;
    },

    /**
     * Injeta o Header, Sidebar e Footer dinamicamente na página
     */
    injectLayout() {
        const user = this.checkAuth();
        if (!user) return;

        // Evita injeção duplicada se o layout já existir na página
        if (document.getElementById('sidebar')) {
            this.updateLayoutInfo(user);
            return;
        }

        // Adiciona Font Awesome para os ícones do footer
        if (!document.getElementById('font-awesome-cdn')) {
            const fa = document.createElement('link');
            fa.id = 'font-awesome-cdn';
            fa.rel = 'stylesheet';
            fa.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css';
            document.head.appendChild(fa);
        }

        const isAdmin = user.email === this.config.adminEmail;
        const body = document.body;

        // 1. Injetar Sidebar e Header (Baseado no Layout.html e LayoutAdmin.html)
        const layoutHTML = `
            <div class="overlay" id="overlay"></div>
            <aside class="sidebar" id="sidebar">
                <button class="menu-btn-close" id="menuBtnClose"><span></span><span></span><span></span></button>
                <div class="profile">
                    <img src="../img/perfil.png" alt="">
                    <h2>${user.nome || (isAdmin ? 'Administrador' : user.email.split('@')[0])}</h2>
                    <p>${isAdmin ? 'Administradora' : (user.cargo || 'Funcionário')}</p>
                </div>
                <nav class="menu">
                    ${isAdmin ? `<a href="Dashboard.html" class="menu-item"><div class="icon-box"><img src="../img/home.png"></div>Dashboard</a>` : ''}
                    ${!isAdmin ? `<a href="baterPonto.html" class="menu-item"><div class="icon-box"><img src="../img/file-signature.png" alt=""></div>Registrar ponto</a>` : ''}
                    <a href="${isAdmin ? this.config.relatorioAdminPage : this.config.relatorioPage}" class="menu-item"><div class="icon-box"><img src="../img/file-chart-line.png" alt=""></div>${isAdmin ? 'Relatórios Gerais' : 'Relatórios'}</a>
                    ${isAdmin ? `<a href="funcionarios.html" class="menu-item"><div class="icon-box"><img src="../img/perfil.png" alt=""></div>Funcionários</a>` : ''}
                    ${isAdmin ? `<a href="cadastro.html" class="menu-item"><div class="icon-box"><img src="../img/file-signature.png" alt=""></div>Novo Cadastro</a>` : ''}
                    ${!isAdmin ? `<a href="justificativa.html" class="menu-item"><div class="icon-box"><img src="../img/drawer-alt.png" alt=""></div>Justificativa</a>` : ''}
                    ${!isAdmin ? `<a href="contracheque.html" class="menu-item"><div class="icon-box"><img src="../img/cheque.png" alt=""></div>Contracheque</a>` : ''}
                    ${!isAdmin ? `<a href="ajuda.html" class="menu-item"><div class="icon-box"><img src="../img/download.png" alt=""></div>Ajuda</a>` : ''}
                    <a href="#" class="menu-item" onclick="HCP.logout(); return false;"><div class="icon-box"><img src="../img/left-from-bracket.png"></div>Sair</a>
                </nav>
            </aside>
            <header class="header">
                <button class="menu-btn" id="menuBtn"><span></span><span></span><span></span></button>
                <div class="top-icons">
                    <a href="${isAdmin ? this.config.dashboardPage : this.config.homePage}" class="top-icon"><img src="../img/home.png" alt=""></a>
                    <a href="${isAdmin ? this.config.relatorioAdminPage : this.config.relatorioPage}" class="top-icon"><img src="../img/pasta.png" alt=""></a>
                    <a href="perfil.html" class="top-icon"><img src="../img/perfil.png" alt=""></a>
                </div>
            </header>
        `;

        const footerHTML = `
            <footer>
                <div class="footer-content">
                    <div class="footer-logo">
                        <img src="../img/file-chart-line.png" style="width:20px; filter: invert(31%) sepia(85%) saturate(1418%) hue-rotate(320deg) brightness(85%) contrast(101%);">
                        HIGH CONTROL POINT
                    </div>
                    <div class="footer-links">
                        <a href="#">Início</a>
                        <a href="#">Sistema</a>
                        <a href="#">Contato</a>
                        <a href="#">Suporte</a>
                    </div>
                    <div class="copyright">© 2026 High Control Point</div>
                </div>
            </footer>
        `;

        // Insere o layout no início e fim do body
        body.insertAdjacentHTML('afterbegin', layoutHTML);
        body.insertAdjacentHTML('beforeend', footerHTML);

        // Configura os eventos do menu (Toggle)
        this.setupMenuEvents();
    },

    setupMenuEvents() {
        const menuBtn = document.getElementById('menuBtn');
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('overlay');
        const menuBtnClose = document.getElementById('menuBtnClose');

        if (menuBtn && sidebar && overlay) {
            menuBtn.addEventListener('click', () => {
                sidebar.classList.toggle('active');
                overlay.classList.toggle('active');
                document.body.classList.toggle('sidebar-open');
            });

            // Evento para o novo botão de fechar interno
            if (menuBtnClose) {
                menuBtnClose.addEventListener('click', () => {
                    overlay.click(); // Reutiliza a lógica de fechar do overlay
                });
            }

            overlay.addEventListener('click', () => {
                sidebar.classList.remove('active');
                overlay.classList.remove('active');
                document.body.classList.remove('sidebar-open');
            });
        }
    },

    /**
     * Inicialização padrão para todas as páginas
     */
    init() {
        this.injectLayout();
        this.updateLayoutInfo(this.checkAuth());
        this.verificarConexaoBanco();

        if (window.location.pathname.includes(this.config.dashboardPage)) {
            this.carregarDashboard();
            this.iniciarInterfacePonto();
        }
        if (window.location.pathname.includes(this.config.funcionariosPage)) {
            this.carregarFuncionarios();
        }
        if (window.location.pathname.includes(this.config.baterPontoPage)) {
            // No longer needed to dynamically set month/year for relatorioPage here
            // as it's handled when relatorioPage itself is initialized.
            this.carregarStatusPonto();
            this.startClock();

            // Esconde a mensagem de sucesso ao trocar o tipo de batida
            const tipoSelect = document.getElementById('ponto-tipo');
            const msgEl = document.getElementById('ponto-sucesso-msg');
            if (tipoSelect && msgEl) {
                tipoSelect.addEventListener('change', () => msgEl.classList.add('hidden'));
            }
        }
        const path = window.location.pathname;
        // Prioriza relatorio-admin para evitar conflito com relatorio.html
        if (path.endsWith(this.config.relatorioAdminPage)) {
            this.carregarRelatoriosAdmin();
        } else if (path.endsWith(this.config.relatorioPage)) {
            this.setDefaultReportFilters();
            this.carregarRelatorios();
        } else if (path.includes(this.config.justificativaPage)) {
            this.carregarJustificativaInfo();
            this.startClock();
        } else if (path.includes(this.config.contrachequePage)) {
            this.setDefaultReportFilters();
            this.carregarContracheque();
            ['relatorio-mes', 'relatorio-ano'].forEach(id => {
                document.getElementById(id)?.addEventListener('change', () => this.carregarContracheque());
            });
        }
    },

    /**
     * Verifica se o servidor Python e o MySQL estão respondendo
     */
    async verificarConexaoBanco() {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();
            
            if (response.ok) {
                console.log('%c[HCP] ✅ Conectado ao PostgreSQL via Flask', 'color: #A4133C; font-weight: bold');
            } else {
                console.error('%c[HCP] ❌ Erro de Banco:', 'color: red', data.mensagem);
            }
        } catch (error) {
            console.warn('%c[HCP] ⚠️ Modo Offline:', 'color: orange', 
                'O servidor Python (server.py) não está respondendo. Verifique se ele foi iniciado no terminal.');
        }
    },

    /**
     * Atualiza informações dinâmicas (nome, cargo) no layout
     */
    updateLayoutInfo(user) {
        if (!user) return;
        const isAdmin = user.email === this.config.adminEmail;
        const nomeExibicao = user.nome || (isAdmin ? 'Administrador' : user.email.split('@')[0]);
        
        const nameElement = document.querySelector('.profile h2');
        const roleElement = document.querySelector('.profile p');
        const welcomeElement = document.querySelector('.welcome-user, .welcome');
        const profileImage = document.querySelector('.sidebar .profile img');
        const profilePhoto = document.getElementById('user-photo-perfil');
        const userPhoto = user.foto || '../img/perfil.png';

        // Elementos específicos do cabeçalho da página de Perfil
        const profileMainName = document.querySelector('.text-center h2.pink-accent');
        const profileMainRole = document.querySelector('.text-center p.text-gray-700');

        if (profileImage) profileImage.src = userPhoto;
        if (profilePhoto) profilePhoto.src = userPhoto;

        // Configuração de interação da foto (apenas na página de perfil)
        const photoOverlay = document.getElementById('foto-overlay');
        const btnRemover = document.getElementById('btn-remover-foto');
        const photoContainer = document.getElementById('photo-container');

        if (photoContainer) {
            if (isAdmin) {
                photoContainer.classList.remove('cursor-pointer');
                photoContainer.removeAttribute('onclick');
                if (photoOverlay) photoOverlay.classList.add('hidden');
                if (btnRemover) btnRemover.classList.add('hidden');
            } else {
                photoContainer.classList.add('cursor-pointer');
                if (photoOverlay) photoOverlay.classList.remove('hidden');
                if (btnRemover) btnRemover.classList.toggle('hidden', !user.foto);
            }
        }

        if (nameElement) nameElement.textContent = nomeExibicao;
        if (roleElement) roleElement.textContent = isAdmin ? 'Administradora' : (user.cargo || 'Funcionário');
        
        if (profileMainName) profileMainName.textContent = nomeExibicao;
        if (profileMainRole) profileMainRole.textContent = isAdmin ? 'Administradora' : (user.cargo || 'Funcionário');
        
        // Atualiza nome na página de Registro de Ponto
        const pontoName = document.getElementById('ponto-nome-funcionario');
        if (pontoName) pontoName.textContent = nomeExibicao;

        const pontoCargo = document.getElementById('ponto-cargo-funcionario');
        if (pontoCargo) pontoCargo.textContent = isAdmin ? 'Administradora' : (user.cargo || 'Funcionário');

        const contraName = document.getElementById('contracheque-nome-funcionario');
        if (contraName) contraName.textContent = nomeExibicao;

        const contraCargo = document.getElementById('contracheque-cargo-funcionario');
        if (contraCargo) contraCargo.textContent = isAdmin ? 'Administradora' : (user.cargo || 'Funcionário');

        const justificativaName = document.getElementById('justificativa-nome-funcionario');
        if (justificativaName) justificativaName.textContent = nomeExibicao;
        const justificativaCargo = document.getElementById('justificativa-cargo-funcionario');
        if (justificativaCargo) justificativaCargo.textContent = isAdmin ? 'Administradora' : (user.cargo || 'Funcionário');
        if (welcomeElement) {
            const primeiroNome = nomeExibicao.split(' ')[0];
            welcomeElement.textContent = `Bem-vindo(a), ${primeiroNome}`;
        }

        // Dispara a busca da localização do aparelho
        this.updateGeolocation();

        // Preenche campos específicos se estiver na página de Perfil
        document.querySelectorAll('.bg-pink-card').forEach(card => {
            const label = card.querySelector('p')?.textContent?.toLowerCase();
            const valueDiv = card.querySelector('.bg-pink-input');
            if (!label || !valueDiv) return;

            if (label.includes('nome')) valueDiv.textContent = user.nome;
            if (label.includes('cargo')) valueDiv.textContent = isAdmin ? 'Administradora' : user.cargo;
            if (label.includes('cpf')) valueDiv.textContent = user.cpf;
            if (label.includes('admissão')) valueDiv.textContent = user.data_admissao;
            if (label.includes('setor')) valueDiv.textContent = user.setor;
        });
    },

    /**
     * Carrega uma nova foto do dispositivo (apenas funcionários)
     * Persiste a foto no banco de dados via API
     */
    async carregarNovaFoto(input) {
        if (input.files && input.files[0]) {
            const reader = new FileReader();
            reader.onload = async (e) => {
                const user = JSON.parse(localStorage.getItem('loggedUser'));
                const fotoBase64 = e.target.result;

                try {
                    const response = await fetch('/api/perfil/foto', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ 
                            id_funcionario: user.id_funcionario,
                            foto: fotoBase64 
                        })
                    });

                    if (response.ok) {
                        user.foto = fotoBase64;
                        localStorage.setItem('loggedUser', JSON.stringify(user));
                        this.updateLayoutInfo(user);
                    } else {
                        alert('Erro ao salvar foto no servidor.');
                    }
                } catch (error) {
                    alert('Falha na comunicação com o servidor.');
                }
            };
            reader.readAsDataURL(input.files[0]);
        }
    },

    /**
     * Remove a foto de perfil atual (apenas funcionários)
     */
    async removerFoto() {
        if (confirm('Deseja remover sua foto de perfil?')) {
            const user = JSON.parse(localStorage.getItem('loggedUser'));
            
            try {
                const response = await fetch('/api/perfil/foto', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        id_funcionario: user.id_funcionario,
                        foto: null 
                    })
                });

                if (response.ok) {
                    delete user.foto;
                    localStorage.setItem('loggedUser', JSON.stringify(user));
                    this.updateLayoutInfo(user);
                } else {
                    alert('Erro ao remover foto do servidor.');
                }
            } catch (error) {
                alert('Falha na comunicação com o servidor.');
            }
        }
    },

    /**
     * Abre um prompt para editar um campo específico do perfil
     */
    async editarCampo(campo) {
        const user = this.checkAuth();
        if (!user) return;

        const labels = { nome: 'Nome', cargo: 'Cargo', cpf: 'CPF', setor: 'Setor' };
        const novoValor = prompt(`Editar ${labels[campo]}:`, user[campo] || '');
        
        if (novoValor !== null && novoValor !== user[campo]) {
            const dadosAtualizados = { ...user, [campo]: novoValor };
            
            try {
                const response = await fetch('/api/perfil/atualizar', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(dadosAtualizados)
                });

                if (response.ok) {
                    localStorage.setItem('loggedUser', JSON.stringify(dadosAtualizados));
                    alert('Alteração salva com sucesso!');
                    location.reload();
                } else {
                    const err = await response.json();
                    alert(err.mensagem || 'Erro ao atualizar');
                }
            } catch (error) {
                alert('Falha na comunicação com o servidor');
            }
        }
    },

    /**
     * Obtém e exibe a localização do aparelho (Cidade/Estado)
     */
    updateGeolocation() {
        const pontoLoc = document.getElementById('ponto-location');
        const justLoc = document.getElementById('justificativa-location');
        const contraLoc = document.getElementById('contracheque-location');

        if ("geolocation" in navigator) {
            navigator.geolocation.getCurrentPosition(async (position) => {
                const { latitude, longitude } = position.coords;
                // Fallback para coordenadas caso o serviço de geocode falhe
                const coordsMsg = `📍 ${latitude.toFixed(2)}, ${longitude.toFixed(2)}`;
                
                if (pontoLoc) pontoLoc.textContent = coordsMsg;
                if (justLoc) justLoc.textContent = coordsMsg;
                if (contraLoc) contraLoc.textContent = coordsMsg;

                try {
                    // Consulta reversa via OpenStreetMap (Gratuito)
                    const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}`);
                    const data = await response.json();
                    const city = data.address.city || data.address.town || data.address.village || "";
                    const state = data.address.state || "";
                    const locationStr = `📍 ${city}${city && state ? ', ' : ''}${state}`;
                    
                    if (pontoLoc) pontoLoc.textContent = locationStr;
                    if (justLoc) justLoc.textContent = locationStr;
                    if (contraLoc) contraLoc.textContent = locationStr;
                } catch (e) { console.log("Geocode failed"); }
            }, () => {
                const msg = "📍 Localização não permitida";
                if (pontoLoc) pontoLoc.textContent = msg;
                if (justLoc) justLoc.textContent = msg;
                if (contraLoc) contraLoc.textContent = msg;
            });
        }
    },

    /**
     * Inicia e atualiza o relógio e a data na página de bater ponto
     */
    startClock() {
        const update = () => {
            const dateEls = document.querySelectorAll('#ponto-data-atual, #justificativa-data-atual');
            const timeEls = document.querySelectorAll('#ponto-hora-atual, #justificativa-hora-atual');
            
            if (dateEls.length === 0 && timeEls.length === 0) return;

            const now = new Date();
            
            const options = { day: 'numeric', month: 'long', year: 'numeric' };
            const dateStr = now.toLocaleDateString('pt-BR', options);
            
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            const timeStr = `${hours}:${minutes}`;

            dateEls.forEach(el => el.textContent = dateStr);
            timeEls.forEach(el => el.textContent = timeStr);
        };
        update();
        setInterval(update, 60000); // Atualiza a cada minuto
    },

    /**
     * Abre prompts para editar todos os campos do perfil de uma vez
     */
    async editarPerfilCompleto() {
        const user = this.checkAuth();
        if (!user) return;

        const novoNome = prompt("Editar Nome Completo:", user.nome || "");
        const novoCargo = prompt("Editar Cargo:", user.cargo || "");
        const novoCpf = prompt("Editar CPF:", user.cpf || "");
        const novoSetor = prompt("Editar Setor:", user.setor || "");

        // Só prossegue se o usuário não cancelar os prompts principais
        if (novoNome !== null && novoCargo !== null) {
            const dadosAtualizados = { 
                ...user, 
                nome: novoNome, 
                cargo: novoCargo, 
                cpf: novoCpf, 
                setor: novoSetor 
            };
            
            try {
                const response = await fetch('/api/perfil/atualizar', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(dadosAtualizados)
                });

                if (response.ok) {
                    localStorage.setItem('loggedUser', JSON.stringify(dadosAtualizados));
                    alert('Perfil atualizado com sucesso!');
                    location.reload();
                } else {
                    alert('Erro ao salvar alterações no banco de dados.');
                }
            } catch (error) {
                alert('Falha na comunicação com o servidor.');
            }
        }
    },

    /**
     * Busca dados reais do banco para o Dashboard
     */
    async carregarDashboard() {
        try {
            const response = await fetch('/api/admin/dashboard-stats');
            const data = await response.json();

            if (!response.ok) throw new Error(data.mensagem);

            // Atualiza os contadores
            if (document.getElementById('stat-funcionarios')) document.getElementById('stat-funcionarios').textContent = data.total_funcionarios;
            if (document.getElementById('stat-presenca')) document.getElementById('stat-presenca').textContent = data.percent_presente;
            if (document.getElementById('stat-justificativas')) document.getElementById('stat-justificativas').textContent = data.justificativas_pendentes;

            // Atualiza Atividade Recente
            const container = document.getElementById('recent-activity-container');
            if (container && data.atividades) {
                container.innerHTML = data.atividades.map(atv => {
                    const iniciais = atv.nome.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
                    const statusClass = atv.status_ponto === 'No Prazo' ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600';
                    
                    return `
                        <div class="flex items-center justify-between border-b border-gray-50 pb-4">
                            <div class="flex items-center gap-4">
                                <div class="w-10 h-10 rounded-full bg-pink-100 flex items-center justify-center text-pink-500 font-bold">${iniciais}</div>
                                <div>
                                    <p class="text-sm font-bold text-gray-800">${atv.nome}</p>
                                    <p class="text-[10px] text-gray-400">Entrada - ${atv.entrada} (${atv.data})</p>
                                </div>
                            </div>
                            <span class="${statusClass} text-[10px] font-bold px-3 py-1 rounded-full uppercase">${atv.status_ponto}</span>
                        </div>
                    `;
                }).join('');
            }
        } catch (error) {
            console.error('Erro ao carregar Dashboard:', error);
            if (tableBody) tableBody.innerHTML = `<tr><td colspan="2" class="p-10 text-center text-red-500">Erro ao carregar registros. Por favor, tente novamente mais tarde.</td></tr>`;
        }
    },

    /**
     * Edita os dados de um funcionário específico da lista
     */
    async editarFuncionario(id) {
        const func = this.listaFuncionarios.find(f => f.id === id);
        if (!func) return;

        const novoNome = prompt("Editar Nome:", func.nome);
        const novoCpf = prompt("Editar CPF:", func.cpf);
        const novoCargo = prompt("Editar Cargo:", func.cargo);
        const novoSetor = prompt("Editar Setor:", func.setor);

        if (novoNome !== null && novoCargo !== null) {
            const dadosAtualizados = { 
                id_funcionario: id,
                nome: novoNome, 
                cargo: novoCargo, 
                cpf: novoCpf, 
                setor: novoSetor
            };
            
            try {
                const response = await fetch('/api/perfil/atualizar', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(dadosAtualizados)
                });

                if (response.ok) {
                    alert('Dados do funcionário atualizados com sucesso!');
                    this.carregarFuncionarios(); // Recarrega a tabela
                } else {
                    alert('Erro ao salvar alterações no banco de dados.');
                }
            } catch (error) {
                alert('Falha na comunicação com o servidor.');
            }
        }
    },

    /**
     * Exclui um funcionário do sistema após confirmação
     */
    async excluirFuncionario(id) {
        if (!confirm('⚠️ Tem certeza que deseja excluir este funcionário?\nEsta ação removerá o acesso ao sistema e os dados cadastrais.')) return;

        try {
            const response = await fetch(`/api/admin/excluir-funcionario/${id}`, {
                method: 'DELETE'
            });

            const data = await response.json();

            if (response.ok) {
                alert('Funcionário excluído com sucesso!');
                this.carregarFuncionarios(); // Atualiza a lista na tela
            } else {
                alert(data.mensagem || 'Erro ao excluir funcionário');
            }
        } catch (error) {
            console.error('Erro na requisição de exclusão:', error);
            alert('Falha na comunicação com o servidor.');
        }
    },

    /**
     * Define os seletores de mês e ano para o período atual na página de relatórios.
     */
    setDefaultReportFilters() {
        const mesSelect = document.getElementById('relatorio-mes');
        const anoSelect = document.getElementById('relatorio-ano');
        const now = new Date();
        const currentMonth = now.getMonth() + 1; // getMonth() é 0-indexed
        const currentYear = now.getFullYear();

        if (mesSelect) {
            mesSelect.value = currentMonth.toString();
        }

        if (anoSelect) {
            // Garante que o ano atual esteja entre as opções, se não, adiciona
            if (!Array.from(anoSelect.options).some(option => option.value === currentYear.toString())) {
                const option = document.createElement('option');
                option.value = currentYear.toString();
                option.textContent = currentYear.toString();
                anoSelect.prepend(option); // Adiciona ao início da lista
            }
            anoSelect.value = currentYear.toString();
        }
    },

    /**
     * Carrega a lista de funcionários na tabela da página funcionários.html
     */
    async carregarFuncionarios() {
        try {
            const response = await fetch('/api/admin/funcionarios');
            const data = await response.json();

            if (!response.ok) throw new Error(data.mensagem);

            this.listaFuncionarios = data; // Armazena os dados para permitir a edição

            const tableBody = document.getElementById('funcionarios-table-body');
            if (tableBody) {
                tableBody.innerHTML = data.map(f => `
                    <tr class="table-row-border hover:bg-white/20 transition-colors">
                        <td class="px-6 py-4 text-sm border-r border-white">${f.nome}</td>
                        <td class="px-6 py-4 text-sm border-r border-white">${f.cpf}</td>
                        <td class="px-6 py-4 text-sm border-r border-white">${f.cargo}</td>
                        <td class="px-6 py-4 text-sm border-r border-white">${f.setor}</td>
                        <td class="px-6 py-4 text-sm border-r border-white">${f.data_admissao}</td>
                        <td class="px-6 py-4 text-center flex justify-center gap-3">
                            <button onclick="window.HCP.editarFuncionario(${f.id})" class="pink-accent hover:scale-110 transition-transform" title="Editar">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                                </svg>
                            </button>
                            <button onclick="HCP.excluirFuncionario(${f.id})" class="text-red-600 hover:scale-110 transition-transform" title="Excluir">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                </svg>
                            </button>
                        </td>
                    </tr>
                `).join('');
            }
        } catch (error) {
            console.error('Erro ao carregar funcionários:', error);
            alert('Não foi possível carregar a lista de funcionários.');
        }
    },

    /**
     * Carrega o histórico de ponto na página relatorio.html
     */
    async carregarRelatorios() {
        const user = this.checkAuth();
        
        console.log('carregarRelatorios: user', user);
        const tableBody = document.getElementById('relatorio-table-body');
        if (!user || !user.id_funcionario) {
            if (tableBody) tableBody.innerHTML = '<tr><td colspan="2" class="p-10 text-center text-red-500">Erro: ID do funcionário não encontrado na sessão.</td></tr>';
            return;
        }

        const mes = document.getElementById('relatorio-mes')?.value;
        const ano = document.getElementById('relatorio-ano')?.value;
        console.log(`carregarRelatorios: mes=${mes}, ano=${ano}`);
        if (tableBody) tableBody.innerHTML = '<tr><td colspan="2" class="p-10 text-center italic">Carregando registros...</td></tr>';

        try {
            let url = `/api/relatorios/${user.id_funcionario}`;
            const params = new URLSearchParams();
            if (mes && mes !== 'undefined') params.append('mes', mes); // Garante que 'undefined' string não seja enviada
            if (ano && ano !== 'undefined') params.append('ano', ano); // Garante que 'undefined' string não seja enviada
            if (params.toString()) url += `?${params.toString()}`;
            console.log('carregarRelatorios: fetch URL', url);

            const response = await fetch(url);
            const data = await response.json();
            
            console.log('carregarRelatorios: data received', data);
            if (!response.ok) throw new Error(data.mensagem);

            if (tableBody) {
                if (data.length === 0) {
                    tableBody.innerHTML = `<tr><td colspan="2" class="p-10 text-center italic">Nenhum registro encontrado para este período.</td></tr>`;
                    return;
                }

                tableBody.innerHTML = data.map(r => `
                    <tr class="table-row-border">
                        <td class="p-3 md:p-4 italic border-r border-white">${r.data}</td>
                        <td class="p-3 md:p-4 leading-relaxed">
                            <div class="flex flex-wrap gap-2">
                                <span>Entrada: ${r.entrada || '--:--'}</span> | <span>Almoço S.: ${r.saida_intervalo || '--:--'}</span> | 
                                <span>Almoço V.: ${r.volta_intervalo || '--:--'}</span> | <span>Saída: ${r.saida || '--:--'}</span>
                            </div>
                            ${r.just_obs ? `
                                <div class="mt-2 p-2 bg-pink-50/50 rounded-lg text-[10px] border border-pink-200 text-pink-900">
                                    <strong class="uppercase">Justificativa [${r.just_status || 'Pendente'}]:</strong> ${r.just_obs}
                                </div>
                            ` : ''}
                        </td>
                    </tr>
                `).join('');
            }
        } catch (error) {
            console.error('Erro ao carregar relatórios:', error);
            if (tableBody) tableBody.innerHTML = `<tr><td colspan="2" class="p-10 text-center text-red-500">Erro ao carregar registros. Verifique sua conexão.</td></tr>`;
        }
    },

    /**
     * Baixa o relatório de ponto do funcionário logado em PDF
     */
    async baixarRelatorioPDF() {
        const user = this.checkAuth();
        if (!user || !user.id_funcionario) return;

        const mes = document.getElementById('relatorio-mes')?.value;
        const ano = document.getElementById('relatorio-ano')?.value;

        console.log(`baixarRelatorioPDF: mes=${mes}, ano=${ano}`);
        try {
            let url = `/api/relatorios/pdf/${user.id_funcionario}`;
            const params = new URLSearchParams();
            
            // Garante que filtros vazios ou 'undefined' não quebrem a URL
            if (mes && mes !== 'undefined') params.append('mes', mes);
            if (ano && ano !== 'undefined') params.append('ano', ano);
            if (params.toString()) url += `?${params.toString()}`;
            console.log('baixarRelatorioPDF: fetch URL', url);

            const response = await fetch(url);
            if (response.ok) {
                console.log('baixarRelatorioPDF: PDF received successfully');
                const blob = await response.blob();
                const downloadUrl = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = downloadUrl;
                a.download = `Relatorio_Ponto_${mes || 'Geral'}.pdf`;
                document.body.appendChild(a);
                a.click();
                a.remove();
            } else {
                alert('Erro ao gerar PDF.');
            }
        } catch (error) {
            alert('Falha na comunicação com o servidor.');
        }
    },
    /**
     * Carrega os relatórios de todos os funcionários para o Admin
     */
    async carregarRelatoriosAdmin() {
        try {
            const response = await fetch('/api/admin/relatorios');
            const data = await response.json();

            if (!response.ok) throw new Error(data.mensagem);

            const tableBody = document.getElementById('relatorio-admin-table-body');
            if (tableBody) {
                tableBody.innerHTML = data.map(r => `
                    <tr class="table-row-border hover:bg-white/20 transition-colors">
                        <td class="px-6 py-4 text-sm border-r border-white font-bold">${r.nome}</td>
                        <td class="px-6 py-4 text-sm border-r border-white">${r.data}</td>
                        <td class="px-6 py-4 text-sm border-r border-white">${r.entrada || '--:--'}</td>
                        <td class="px-6 py-4 text-sm border-r border-white">${r.saida_intervalo || '--:--'}</td>
                        <td class="px-6 py-4 text-sm border-r border-white">${r.volta_intervalo || '--:--'}</td>
                        <td class="px-6 py-4 text-sm">${r.saida || '--:--'}</td>
                    </tr>
                `).join('');
            }
        } catch (error) {
            console.error('Erro ao carregar relatórios admin:', error);
            const tableBody = document.getElementById('relatorio-admin-table-body');
            if (tableBody) tableBody.innerHTML = `<tr><td colspan="6" class="p-4 text-center text-red-500">Erro ao carregar dados.</td></tr>`;
        }
    },

    /**
     * Baixa o relatório geral de todos os funcionários em PDF
     */
    async baixarRelatorioGeralPDF() {
        try {
            const response = await fetch('/api/admin/relatorios/pdf');
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = `Relatorio_Geral_Pontos_${new Date().toLocaleDateString().replace(/\//g, '-')}.pdf`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
            } else {
                alert('Erro ao gerar PDF do relatório geral.');
            }
        } catch (error) {
            console.error('Erro:', error);
            alert('Falha na comunicação com o servidor.');
        }
    },

    /**
     * Carrega o status do ponto para o dia de hoje
     */
    async carregarStatusPonto() {
        const user = this.checkAuth();
        if (!user || !user.id_funcionario) return;
        try {
            const response = await fetch(`/api/ponto/status/${user.id_funcionario}`);
            const data = await response.json();
            
            const campos = {
                'ponto-entrada': data?.entrada,
                'ponto-intervalo-s': data?.saida_intervalo,
                'ponto-intervalo-v': data?.volta_intervalo,
                'ponto-saida': data?.saida
            };

            for (let id in campos) {
                const el = document.getElementById(id);
                if (el) el.textContent = campos[id] || '--:--';
            }

            const btn = document.getElementById('btn-bater-ponto');
            if (btn) {
                if (data?.entrada && data?.saida_intervalo && data?.volta_intervalo && data?.saida) {
                    btn.disabled = true;
                    btn.textContent = 'Jornada Concluída';
                }
            }
        } catch (error) { console.error('Erro ao carregar status do ponto:', error); }
    },

    /**
     * Envia solicitação para bater o ponto
     */
    async baterPonto() {
        const user = this.checkAuth();
        if (!user || !user.id_funcionario) return alert('Funcionário não identificado.');
        
        const tipoSelect = document.getElementById('ponto-tipo');
        const tipo = tipoSelect ? tipoSelect.value : 'Entrada';

        try {
            const response = await fetch('/api/ponto/registrar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    id_funcionario: user.id_funcionario,
                    tipo: tipo
                })
            });
            const data = await response.json();
            
            if (response.ok) {
                const msgEl = document.getElementById('ponto-sucesso-msg');
                if (msgEl) msgEl.classList.remove('hidden');
                this.carregarStatusPonto();
            } else {
                alert(data.mensagem || 'Erro ao registrar ponto.');
            }
        } catch (error) { alert('Erro ao registrar ponto.'); }
    },

    /**
     * Busca os dados financeiros do funcionário para o contracheque
     */
    async carregarContracheque() {
        const user = this.checkAuth();
        if (!user || !user.id_funcionario) {
            console.error('Contracheque: Funcionário não vinculado.');
            return;
        }

        const mes = document.getElementById('relatorio-mes')?.value;
        const ano = document.getElementById('relatorio-ano')?.value;

        try {
            const response = await fetch(`/api/contracheque/${user.id_funcionario}?mes=${mes}&ano=${ano}`);
            const data = await response.json();
            
            if (response.ok) {
                const formatarMoeda = (valor) => valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
                
                const elBruto = document.getElementById('contracheque-bruto');
                const elLiquido = document.getElementById('contracheque-liquido');
                const elDescontos = document.getElementById('contracheque-descontos');
                const elListaItens = document.getElementById('contracheque-lista-descontos');

                if (elBruto) elBruto.textContent = formatarMoeda(data.salario_bruto);
                if (elLiquido) elLiquido.textContent = formatarMoeda(data.salario_liquido);
                if (elDescontos) elDescontos.textContent = formatarMoeda(data.descontos);

                // Se não houver itens detalhados, limpa a lista
                if (elListaItens && (!data.itens_detalhados || data.itens_detalhados.length === 0)) {
                    elListaItens.innerHTML = '<p class="text-center text-gray-400 py-4">Nenhum desconto registrado para este período.</p>';
                }

                // Preenche o espaço abaixo com a lista de descontos calculados
                if (elListaItens && data.itens_detalhados) {
                    elListaItens.innerHTML = data.itens_detalhados.map(item => `
                        <div class="flex justify-between border-b border-pink-100 py-2">
                            <span class="text-gray-600">${item.descricao}</span>
                            <span class="text-red-500 font-bold">- ${formatarMoeda(item.valor)}</span>
                        </div>
                    `).join('') || '<p class="text-center text-gray-400 py-4">Nenhum desconto registrado para este período.</p>';
                }
            } else {
                console.error('Erro ao buscar dados do contracheque:', data.mensagem);
            }
        } catch (error) {
            console.error('Falha na comunicação ao carregar contracheque:', error);
        }
    },

    /**
     * Baixa o contracheque do funcionário logado em PDF
     */
    async baixarContrachequePDF() {
        const user = this.checkAuth();
        if (!user || !user.id_funcionario) return;

        const mesInput = document.getElementById('relatorio-mes')?.value;
        const anoInput = document.getElementById('relatorio-ano')?.value;
        const mes = (mesInput && mesInput !== 'undefined') ? mesInput : (new Date().getMonth() + 1);
        const ano = (anoInput && anoInput !== 'undefined') ? anoInput : new Date().getFullYear();

        try {
            let url = `/api/contracheque/pdf/${user.id_funcionario}`;
            const params = new URLSearchParams();
            params.append('mes', mes);
            params.append('ano', ano);
            url += `?${params.toString()}`;

            const response = await fetch(url);
            if (response.ok) {
                const blob = await response.blob();
                const downloadUrl = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = downloadUrl;
                a.download = `Contracheque_${mes}_${ano}.pdf`;
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(downloadUrl);
            } else {
                const errorData = await response.json();
                alert('Erro ao gerar PDF: ' + (errorData.mensagem || 'Erro no servidor'));
            }
        } catch (error) {
            alert('Falha na comunicação com o servidor.');
        }
    },

    /**
     * Gera a folha de pagamento mensal (Admin)
     */
    async gerarFolha() {
        if (!confirm('Deseja processar a folha de pagamento de todos os funcionários para o mês atual?')) return;

        try {
            const response = await fetch('/api/admin/gerar-folha', { method: 'POST' });
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = `Folha_Mensal_${new Date().getMonth() + 1}_${new Date().getFullYear()}.pdf`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                alert('Folha de pagamento gerada e baixada com sucesso!');
            } else {
                const data = await response.json();
                alert(data.mensagem || 'Erro ao processar folha.');
            }
        } catch (error) {
            console.error('Erro:', error);
            alert('Falha ao processar folha de pagamento.');
        }
    },

    /**
     * Carrega informações do funcionário na página de justificativa
     */
    carregarJustificativaInfo() {
        const user = this.checkAuth();
        if (!user) return;

        const isAdmin = user.email === this.config.adminEmail;
        const nomeExibicao = user.nome || (isAdmin ? 'Administrador' : user.email.split('@')[0]);

        const justificativaName = document.getElementById('justificativa-nome-funcionario');
        if (justificativaName) justificativaName.textContent = nomeExibicao;
        const justificativaCargo = document.getElementById('justificativa-cargo-funcionario');
        if (justificativaCargo) justificativaCargo.textContent = isAdmin ? 'Administradora' : (user.cargo || 'Funcionário');

        // Preencher data de início com a data de hoje no formato YYYY-MM-DD
        const dataInicioInput = document.getElementById('data_inicio');
        if (dataInicioInput && !dataInicioInput.value) {
            dataInicioInput.value = new Date().toISOString().split('T')[0];
        }
    },

    /**
     * Envia a justificativa para o servidor
     */
    async enviarJustificativa() {
        const user = this.checkAuth();
        if (!user || !user.id_funcionario) return alert('Funcionário não identificado.');

        const tipo = document.getElementById('tipo_justificativa')?.value;
        const dataFalta = document.getElementById('data_inicio')?.value; 
        const motivo = document.getElementById('observacao')?.value;
        const compensacao = document.getElementById('compensar_horas')?.checked ? 'Sim' : 'Não';

        if (!tipo || !dataFalta || !motivo) return alert('Por favor, preencha o tipo, a data e o motivo da justificativa.');

        try {
            const response = await fetch('/api/justificativa/registrar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    id_funcionario: user.id_funcionario, 
                    tipo,
                    data_falta: dataFalta,
                    motivo,
                    compensacao
                })
            });
            const data = await response.json();
            if (response.ok) {
                alert(data.mensagem);
                document.getElementById('justificativa-form').reset(); // Limpa o formulário
                document.getElementById('justificativa-sucesso-msg').classList.remove('hidden'); // Mostra mensagem de sucesso
            } else {
                alert(data.mensagem || 'Erro ao enviar justificativa.');
            }
        } catch (error) {
            alert('Falha na comunicação com o servidor.');
        }
    },

    /**
     * Placeholder para visualização de alertas
     */
    async verAlertas() {
        try {
            const response = await fetch('/api/admin/alertas');
            const atrasos = await response.json();
            
            if (atrasos.length === 0) {
                alert('Nenhum atraso detectado hoje até o momento.');
                return;
            }

            let mensagem = `⚠️ Alertas de Atraso (${atrasos.length}):\n\n`;
            atrasos.forEach(a => {
                mensagem += `- ${a.nome}: Entrada às ${a.entrada}\n`;
            });
            
            alert(mensagem);
        } catch (error) {
            console.error('Erro:', error);
            alert('Falha ao buscar alertas de atraso.');
        }
    },

    /**
     * Ajusta o Layout (Sidebar) com base no cargo
     */
    initLayout() {
        const user = this.checkAuth();
        if (!user) return;

        const isAdmin = user.email === this.config.adminEmail;
        
        // Esconde itens administrativos se não for admin
        document.querySelectorAll('.admin-only').forEach(item => {
            item.style.setProperty('display', isAdmin ? 'flex' : 'none', 'important');
        });

        // Atualiza nome no perfil e na Home
        const userName = user.email.split('@')[0];
        const profileName = document.querySelector('.profile h2, .welcome-user');
        if (profileName) {
            profileName.textContent = isAdmin ? 'Lana Benett' : userName.charAt(0).toUpperCase() + userName.slice(1);
        }
    }
};

// Disponibiliza globalmente para os formulários HTML
window.HCP = HCP_App;