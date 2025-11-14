/**
 * Dashboard SLA - JavaScript com ApexCharts
 */

// Variáveis globais
let charts = {
    colunas: null,
    pizza: null,
    executores: null,
    locais: null
};

let mesAtual = new Date().getMonth() + 1;
let anoAtual = new Date().getFullYear();
// Filtro fixo: apenas dados do diretor executivo MARCOS NASCIMENTO PEDREIRA
let filtrosAtivos = {
    'diretor_executivo': 'MARCOS NASCIMENTO PEDREIRA'
};

// Filtro de cross-filtering (drill-down interativo)
let filtroCross = null;

// Variáveis de auto-refresh
let autoRefreshInterval = null;
let autoRefreshEnabled = true;
let ultimaAtualizacao = null;
const INTERVALO_ATUALIZACAO = 600000; // 10 minutos em ms

// Cache para os 5 meses consolidados (não precisam atualizar a cada 10min)
let cacheConsolidado = {
    dados: {},
    filtrosCache: null
};

// Timer para debounce
let debounceTimer = null;

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    inicializarSelectMes();
    inicializarSelect2();
    inicializarEventos();
    carregarDashboard();
    iniciarAutoRefresh();
});

/**
 * Inicializa select de mês - mostra apenas últimos 6 meses
 */
function inicializarSelectMes() {
    const select = document.getElementById('selectMes');
    const meses = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ];
    
    const hoje = new Date();
    const ultimos6Meses = obterUltimos6Meses();
    
    // Adiciona apenas os últimos 6 meses
    ultimos6Meses.forEach((mesAno, index) => {
        const option = document.createElement('option');
        option.value = `${mesAno.mes}-${mesAno.ano}`;
        option.text = `${meses[mesAno.mes - 1]}/${mesAno.ano}`;
        
        // Mês atual é selecionado por padrão
        if (index === 0) {
            option.selected = true;
        }
        
        select.appendChild(option);
    });
}

/**
 * Retorna array com os últimos 6 meses (mês atual + 5 anteriores)
 */
function obterUltimos6Meses() {
    const ultimos = [];
    const hoje = new Date();
    
    for (let i = 0; i < 6; i++) {
        const data = new Date(hoje.getFullYear(), hoje.getMonth() - i, 1);
        ultimos.push({
            mes: data.getMonth() + 1,
            ano: data.getFullYear()
        });
    }
    
    return ultimos;
}

/**
 * Inicializa Select2 nos filtros (com pesquisa)
 */
function inicializarSelect2() {
    // Aplica Select2 em todos os selects do formulário de filtros, exceto o diretor executivo (desabilitado)
    $('#formFiltros select:not([disabled])').select2({
        placeholder: 'Selecione...',
        allowClear: true,
        language: {
            noResults: function() {
                return "Nenhum resultado encontrado";
            },
            searching: function() {
                return "Buscando...";
            }
        }
    });
    
    // Reaplica filtros quando select2 mudar
    $('#formFiltros select:not([disabled])').on('select2:select select2:clear', function() {
        aplicarFiltrosDebounced();
    });
    
    // Filtro em cascata: Gerente → Supervisores
    $('select[name="gerente"]').on('select2:select', function() {
        const gerente = $(this).val();
        if (gerente) {
            carregarSupervisoresPorGerente(gerente);
        }
    });
    
    $('select[name="gerente"]').on('select2:clear', function() {
        // Reseta o select de supervisores para todos
        resetarSelectSupervisor();
    });
}

/**
 * Carrega supervisores filtrados por gerente
 */
async function carregarSupervisoresPorGerente(gerente) {
    try {
        const response = await fetch(`/dashboard/api/supervisores-por-gerente?gerente=${encodeURIComponent(gerente)}`);
        const result = await response.json();
        
        if (result.success) {
            const selectSupervisor = $('select[name="supervisor"]');
            
            // Limpa opções atuais (mantém a primeira opção vazia)
            selectSupervisor.empty().append('<option value="">Todos</option>');
            
            // Adiciona supervisores filtrados
            result.data.forEach(supervisor => {
                selectSupervisor.append(new Option(supervisor, supervisor, false, false));
            });
            
            // Atualiza o Select2
            selectSupervisor.trigger('change');
        }
    } catch (error) {
        console.error('Erro ao carregar supervisores:', error);
    }
}

/**
 * Reseta o select de supervisores para todos os valores originais
 */
function resetarSelectSupervisor() {
    // Recarrega a página para restaurar todos os valores originais
    // Alternativa: manter os valores originais em cache e restaurá-los
    location.reload();
}

/**
 * Inicializa eventos
 */
function inicializarEventos() {
    // Botão filtros
    document.getElementById('btnFiltros').addEventListener('click', function() {
        const panel = document.getElementById('panelFiltros');
        panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
    });
    
    // Change no select de mês
    document.getElementById('selectMes').addEventListener('change', function() {
        const mesAno = this.value.split('-');
        mesAtual = parseInt(mesAno[0]);
        anoAtual = parseInt(mesAno[1]);
        carregarDashboard();
        atualizarBadgeStatus(); // Atualiza badge ao trocar de mês
    });
    
    // Limites de executores e locais
    document.getElementById('selectLimitExecutores').addEventListener('change', function() {
        carregarChartExecutores();
    });
    
    document.getElementById('selectLimitLocais').addEventListener('change', function() {
        carregarChartLocais();
    });
    
    // Controles de auto-refresh
    document.getElementById('btnPausar').addEventListener('click', pausarAutoRefresh);
    document.getElementById('btnDespausar').addEventListener('click', retomarAutoRefresh);
    document.getElementById('btnForcarAtualizacao').addEventListener('click', forcarAtualizacao);
    
    // Event listeners para filtros com debounce
    const formFiltros = document.getElementById('formFiltros');
    if (formFiltros) {
        // Adiciona debounce em todos inputs e selects, EXCETO o campo CR
        const inputs = formFiltros.querySelectorAll('input:not([name="cr"]), select');
        inputs.forEach(input => {
            input.addEventListener('input', aplicarFiltrosDebounced);
            input.addEventListener('change', aplicarFiltrosDebounced);
        });
    }
}

/**
 * Função debounce para evitar múltiplas chamadas seguidas
 */
function debounce(func, delay) {
    return function(...args) {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => func.apply(this, args), delay);
    };
}

/**
 * Aplica filtros (com debounce de 300ms)
 */
const aplicarFiltrosDebounced = debounce(function() {
    const form = document.getElementById('formFiltros');
    const formData = new FormData(form);
    
    // Inicia com o filtro fixo do diretor executivo
    filtrosAtivos = {
        'diretor_executivo': 'MARCOS NASCIMENTO PEDREIRA'
    };
    
    // Adiciona os demais filtros do formulário
    for (let [key, value] of formData.entries()) {
        if (value && key !== 'diretor_executivo') {  // Ignora diretor_executivo do form pois já está fixo
            filtrosAtivos[key] = value;
        }
    }
    
    // Limpa cache ao mudar filtros
    limparCache();
    carregarDashboard();
}, 300);

/**
 * Aplica filtros (versão imediata para botão)
 */
function aplicarFiltros() {
    // Cancela debounce pendente
    clearTimeout(debounceTimer);
    
    const form = document.getElementById('formFiltros');
    const formData = new FormData(form);
    
    // Inicia com o filtro fixo do diretor executivo
    filtrosAtivos = {
        'diretor_executivo': 'MARCOS NASCIMENTO PEDREIRA'
    };
    
    // Adiciona os demais filtros do formulário
    for (let [key, value] of formData.entries()) {
        if (value && key !== 'diretor_executivo') {  // Ignora diretor_executivo do form pois já está fixo
            filtrosAtivos[key] = value;
        }
    }
    
    // Limpa filtro cross ao mudar filtros normais
    filtroCross = null;
    atualizarBadgeFiltroCross();
    
    // Limpa cache ao mudar filtros
    limparCache();
    carregarDashboard();
}

/**
 * Limpa filtros
 */
function limparFiltros() {
    document.getElementById('formFiltros').reset();
    
    // Mantém apenas o filtro fixo do diretor executivo
    filtrosAtivos = {
        'diretor_executivo': 'MARCOS NASCIMENTO PEDREIRA'
    };
    
    // Limpa filtro cross também
    filtroCross = null;
    atualizarBadgeFiltroCross();
    
    // Limpa cache ao limpar filtros
    limparCache();
    carregarDashboard();
}

/**
 * Limpa o cache de dados consolidados
 */
function limparCache() {
    cacheConsolidado.dados = {};
    cacheConsolidado.filtrosCache = null;
    console.log('Cache consolidado limpo');
}

/**
 * Monta query string com filtros
 */
function montarQueryString() {
    const params = new URLSearchParams();
    params.append('mes', mesAtual);
    params.append('ano', anoAtual);
    
    // Filtros normais
    for (let [key, value] of Object.entries(filtrosAtivos)) {
        params.append(key, value);
    }
    
    // Filtro cross (drill-down interativo)
    if (filtroCross) {
        params.append('cr', filtroCross.cr);
    }
    
    return params.toString();
}

/**
 * Aplica filtro cross (drill-down) ao clicar em elemento do heatmap
 */
function aplicarFiltroCross(cr, contrato) {
    filtroCross = { cr, contrato };
    
    // Atualiza badge visual
    atualizarBadgeFiltroCross();
    
    // Recarrega apenas os gráficos (não o heatmap)
    Promise.all([
        carregarCards(),
        carregarChartColunas(),
        carregarChartPizza(),
        carregarChartExecutores(),
        carregarChartLocais()
    ]);
}

/**
 * Limpa filtro cross
 */
function limparFiltroCross() {
    filtroCross = null;
    
    // Remove badge visual
    atualizarBadgeFiltroCross();
    
    // Remove destaque visual das linhas do heatmap
    const tbody = document.getElementById('heatmapBody');
    if (tbody) {
        tbody.querySelectorAll('tr').forEach(row => {
            row.classList.remove('selected');
        });
    }
    
    // Recarrega apenas os gráficos
    Promise.all([
        carregarCards(),
        carregarChartColunas(),
        carregarChartPizza(),
        carregarChartExecutores(),
        carregarChartLocais()
    ]);
}

/**
 * Atualiza badge de filtro cross
 */
function atualizarBadgeFiltroCross() {
    let badgeContainer = document.getElementById('badgeFiltroCrossContainer');
    
    if (!badgeContainer) {
        // Cria container se não existir
        const headerDiv = document.querySelector('.d-flex.justify-content-between.align-items-center.mb-4 > div:first-child');
        badgeContainer = document.createElement('div');
        badgeContainer.id = 'badgeFiltroCrossContainer';
        badgeContainer.className = 'mt-2';
        headerDiv.appendChild(badgeContainer);
    }
    
    if (filtroCross) {
        badgeContainer.innerHTML = `
            <div class="d-flex align-items-center gap-2">
                <span class="badge bg-warning text-dark" style="font-size: 0.9rem;">
                    🔍 Filtrado: CR ${filtroCross.cr} - ${filtroCross.contrato}
                </span>
                <button class="btn btn-sm btn-outline-danger" onclick="limparFiltroCross()" title="Limpar filtro">
                    <i class="bi bi-x-circle"></i> Limpar
                </button>
            </div>
        `;
    } else {
        badgeContainer.innerHTML = '';
    }
}

/**
 * Mostra loading
 */
function mostrarLoading() {
    document.getElementById('loadingOverlay').style.display = 'block';
}

/**
 * Esconde loading
 */
function esconderLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
}

/**
 * Carrega dashboard completo
 */
async function carregarDashboard() {
    mostrarLoading();
    
    try {
        await Promise.all([
            carregarCards(),
            carregarChartColunas(),
            carregarChartPizza(),
            carregarHeatmap(),
            carregarChartExecutores(),
            carregarChartLocais()
        ]);
        
        // Atualiza timestamp após carregar
        atualizarTimestamp();
        
    } catch (error) {
        console.error('Erro ao carregar dashboard:', error);
        alert('Erro ao carregar dashboard: ' + error.message);
    } finally {
        esconderLoading();
    }
}

/**
 * Inicia auto-refresh
 * Atualiza apenas o mês atual (últimos 5 meses são consolidados)
 */
function iniciarAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
    
    autoRefreshInterval = setInterval(function() {
        if (autoRefreshEnabled) {
            const hoje = new Date();
            const mesAtualSistema = hoje.getMonth() + 1;
            const anoAtualSistema = hoje.getFullYear();
            
            // Só atualiza se estiver visualizando o mês atual
            if (mesAtual === mesAtualSistema && anoAtual === anoAtualSistema) {
                console.log('Auto-refresh: atualizando apenas mês atual...');
                carregarDashboard();
            } else {
                console.log('Auto-refresh: visualizando mês consolidado, não há necessidade de atualizar');
            }
        }
    }, INTERVALO_ATUALIZACAO);
    
    autoRefreshEnabled = true;
    atualizarBadgeStatus();
}

/**
 * Pausa auto-refresh
 */
function pausarAutoRefresh() {
    autoRefreshEnabled = false;
    atualizarBadgeStatus();
    
    // Troca visibilidade dos botões
    document.getElementById('btnPausar').style.display = 'none';
    document.getElementById('btnDespausar').style.display = 'block';
}

/**
 * Retoma auto-refresh
 */
function retomarAutoRefresh() {
    autoRefreshEnabled = true;
    atualizarBadgeStatus();
    
    // Atualiza imediatamente
    carregarDashboard();
    
    // Troca visibilidade dos botões
    document.getElementById('btnPausar').style.display = 'block';
    document.getElementById('btnDespausar').style.display = 'none';
}

/**
 * Força atualização imediata
 */
function forcarAtualizacao() {
    console.log('Forçando atualização manual...');
    carregarDashboard();
    
    // Reseta o timer
    if (autoRefreshEnabled) {
        iniciarAutoRefresh();
    }
}

/**
 * Atualiza timestamp de última atualização
 */
function atualizarTimestamp() {
    ultimaAtualizacao = new Date();
    
    const dia = String(ultimaAtualizacao.getDate()).padStart(2, '0');
    const mes = String(ultimaAtualizacao.getMonth() + 1).padStart(2, '0');
    const ano = ultimaAtualizacao.getFullYear();
    const hora = String(ultimaAtualizacao.getHours()).padStart(2, '0');
    const minuto = String(ultimaAtualizacao.getMinutes()).padStart(2, '0');
    const segundo = String(ultimaAtualizacao.getSeconds()).padStart(2, '0');
    
    const dataFormatada = `${dia}/${mes}/${ano} às ${hora}:${minuto}:${segundo}`;
    
    document.getElementById('timestampUltima').textContent = `Última atualização: ${dataFormatada}`;
}

/**
 * Atualiza badge de status
 */
function atualizarBadgeStatus() {
    const badge = document.getElementById('badgeStatus');
    
    if (!autoRefreshEnabled) {
        badge.className = 'badge bg-danger';
        badge.textContent = '🔴 Atualização Pausada';
        return;
    }
    
    // Verifica se está no mês atual ou em mês consolidado
    const hoje = new Date();
    const mesAtualSistema = hoje.getMonth() + 1;
    const anoAtualSistema = hoje.getFullYear();
    const ehMesAtual = (mesAtual === mesAtualSistema && anoAtual === anoAtualSistema);
    
    if (ehMesAtual) {
        badge.className = 'badge bg-success status-ativo';
        badge.textContent = '🟢 Atualizando a cada 10min';
    } else {
        badge.className = 'badge bg-info';
        badge.textContent = '📊 Mês Consolidado (não atualiza)';
    }
}

/**
 * Carrega cards de resumo
 */
async function carregarCards() {
    const queryString = montarQueryString();
    
    const response = await fetch(`/dashboard/api/resumo?${queryString}`);
    const result = await response.json();
    
    if (result.success) {
        const data = result.data;
        document.getElementById('cardEmAberto').textContent = data.em_aberto.toLocaleString('pt-BR');
        document.getElementById('cardIniciadas').textContent = data.iniciadas.toLocaleString('pt-BR');
        document.getElementById('cardFinalizadas').textContent = data.finalizadas.toLocaleString('pt-BR');
        document.getElementById('cardNaoRealizadas').textContent = data.nao_realizadas.toLocaleString('pt-BR');
    }
}

/**
 * Carrega gráfico de colunas empilhadas (com 4 categorias)
 */
async function carregarChartColunas() {
    const queryString = montarQueryString();
    
    const response = await fetch(`/dashboard/api/tarefas-mes?${queryString}`);
    const result = await response.json();
    
    if (result.success) {
        const data = result.data;
        
        // Filtra apenas até hoje se for mês atual
        const hoje = new Date();
        const ehMesAtual = (anoAtual === hoje.getFullYear() && mesAtual === (hoje.getMonth() + 1));
        
        const dataFiltrada = ehMesAtual 
            ? data.filter(item => {
                const dia = parseInt(item.dia.split('-')[2]);
                return dia <= hoje.getDate();
              })
            : data;
        
        // Prepara categorias (dias do mês)
        // Extrai o dia diretamente da string 'YYYY-MM-DD'
        const categorias = dataFiltrada.map(item => {
            return parseInt(item.dia.split('-')[2]);
        });
        
        // Prepara dados por série
        const finalizadas = dataFiltrada.map(item => item.finalizadas);
        const naoRealizadas = dataFiltrada.map(item => item.nao_realizadas);
        const emAberto = dataFiltrada.map(item => item.em_aberto);
        const iniciadas = dataFiltrada.map(item => item.iniciadas);
        
        // Destroi gráfico anterior se existir
        if (charts.colunas) {
            charts.colunas.destroy();
        }
        
        // Opções do gráfico empilhado
        const options = {
            series: [
                {
                    name: 'Finalizadas',
                    data: finalizadas
                },
                {
                    name: 'Não Realizadas',
                    data: naoRealizadas
                },
                {
                    name: 'Em Aberto',
                    data: emAberto
                },
                {
                    name: 'Iniciadas',
                    data: iniciadas
                }
            ],
            chart: {
                type: 'bar',
                height: 350,
                stacked: true,
                toolbar: {
                    show: true
                }
            },
            plotOptions: {
                bar: {
                    borderRadius: 0,
                    dataLabels: {
                        position: 'center'
                    }
                }
            },
            dataLabels: {
                enabled: false
            },
            xaxis: {
                categories: categorias,
                title: {
                    text: 'Dia do Mês'
                }
            },
            yaxis: {
                title: {
                    text: 'Quantidade de Tarefas'
                }
            },
            colors: ['#28a745', '#dc3545', '#17a2b8', '#ffc107'],
            legend: {
                position: 'top',
                horizontalAlign: 'center'
            },
            tooltip: {
                y: {
                    formatter: function(val) {
                        return val + ' tarefas';
                    }
                }
            }
        };
        
        charts.colunas = new ApexCharts(document.querySelector('#chartColunas'), options);
        charts.colunas.render();
    }
}

/**
 * Carrega gráfico de pizza
 */
async function carregarChartPizza() {
    const queryString = montarQueryString();
    
    const response = await fetch(`/dashboard/api/pizza?${queryString}`);
    const result = await response.json();
    
    if (result.success) {
        const data = result.data;
        
        // Prepara dados
        const labels = data.map(item => item.status);
        const valores = data.map(item => item.total);
        const cores = data.map(item => item.cor);
        
        // Destroi gráfico anterior
        if (charts.pizza) {
            charts.pizza.destroy();
        }
        
        // Opções do gráfico
        const options = {
            series: valores,
            chart: {
                type: 'donut',
                height: 350
            },
            labels: labels,
            colors: cores,
            legend: {
                position: 'bottom'
            },
            dataLabels: {
                enabled: true,
                formatter: function(val) {
                    return val.toFixed(1) + '%';
                }
            },
            tooltip: {
                y: {
                    formatter: function(val) {
                        return val.toLocaleString('pt-BR') + ' tarefas';
                    }
                }
            }
        };
        
        charts.pizza = new ApexCharts(document.querySelector('#chartPizza'), options);
        charts.pizza.render();
    }
}

/**
 * Carrega heatmap com CR x Dias do Mês
 */
async function carregarHeatmap() {
    const queryString = montarQueryString();
    const tbody = document.getElementById('heatmapBody');
    const thead = document.getElementById('heatmapHead');
    
    try {
        const response = await fetch(`/dashboard/api/heatmap-dias?${queryString}`);
        const result = await response.json();
        
        if (!result.success) {
            console.error('Erro ao carregar heatmap:', result.error);
            tbody.innerHTML = '<tr><td colspan="3" class="text-center text-danger">Erro ao carregar dados: ' + (result.error || 'Erro desconhecido') + '</td></tr>';
            return;
        }
        
        const data = result.data;
        const mes = result.mes;
        const ano = result.ano;
        
        // Calcula quantos dias mostrar (até hoje se for mês atual)
        const hoje = new Date();
        const ultimoDiaMes = new Date(ano, mes, 0).getDate();
        let ultimoDia = ultimoDiaMes;
        
        // Se é o mês atual, mostrar só até hoje
        if (ano === hoje.getFullYear() && mes === (hoje.getMonth() + 1)) {
            ultimoDia = Math.min(hoje.getDate(), ultimoDiaMes);
        }
        
        // Monta cabeçalho da tabela
        let headerHtml = '<tr><th>CR</th><th>Contrato</th>';
        for (let dia = 1; dia <= ultimoDia; dia++) {
            headerHtml += `<th>${dia}</th>`;
        }
        headerHtml += '</tr>';
        thead.innerHTML = headerHtml;
        
        // Monta corpo da tabela
        tbody.innerHTML = '';
        
        if (data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="${ultimoDia + 2}" class="text-center">Nenhum dado encontrado</td></tr>`;
            return;
        }
        
        data.forEach(item => {
            const tr = document.createElement('tr');
            let rowHtml = `<td><strong>${item.cr}</strong></td><td>${item.contrato}</td>`;
            
            // Para cada dia do mês
            for (let dia = 1; dia <= ultimoDia; dia++) {
                const porcentagem = item.dias[dia];
                
                if (porcentagem !== undefined) {
                    // Determina cor baseada na porcentagem
                    let corFundo = '#e9ecef'; // cinza (sem dados)
                    let corTexto = '#666';
                    
                    if (porcentagem > 90) {
                        corFundo = '#28a745'; // verde
                        corTexto = '#fff';
                    } else if (porcentagem >= 65) {
                        corFundo = '#ffc107'; // amarelo
                        corTexto = '#000';
                    } else {
                        corFundo = '#dc3545'; // vermelho
                        corTexto = '#fff';
                    }
                    
                    rowHtml += `<td style="background-color: ${corFundo}; color: ${corTexto}; font-weight: bold; text-align: center;">${porcentagem.toFixed(0)}%</td>`;
                } else {
                    // Sem dados
                    rowHtml += '<td style="background-color: #e9ecef;"></td>';
                }
            }
            
            tr.innerHTML = rowHtml;
            
            // Adiciona estilo de hover e cursor pointer
            tr.style.cursor = 'pointer';
            tr.style.transition = 'all 0.2s ease';
            tr.title = 'Clique para filtrar todos os gráficos por este CR';
            
            // Destaca linha se for o CR/Contrato filtrado
            if (filtroCross && filtroCross.cr === item.cr && filtroCross.contrato === item.contrato) {
                tr.classList.add('selected');
            }
            
            // Event listener para clique
            tr.addEventListener('click', function() {
                aplicarFiltroCross(item.cr, item.contrato);
                
                // Remove destaque de todas as linhas
                tbody.querySelectorAll('tr').forEach(row => {
                    row.classList.remove('selected');
                });
                
                // Destaca linha clicada
                this.classList.add('selected');
            });
            
            // Hover effect
            tr.addEventListener('mouseenter', function() {
                if (!filtroCross || filtroCross.cr !== item.cr || filtroCross.contrato !== item.contrato) {
                    this.style.backgroundColor = '#f8f9fa';
                }
            });
            
            tr.addEventListener('mouseleave', function() {
                if (!filtroCross || filtroCross.cr !== item.cr || filtroCross.contrato !== item.contrato) {
                    this.style.backgroundColor = '';
                }
            });
            
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error('Erro ao carregar heatmap:', error);
        tbody.innerHTML = '<tr><td colspan="3" class="text-center text-danger">Erro ao carregar heatmap. Verifique o console para mais detalhes.</td></tr>';
    }
}

/**
 * Carrega gráfico de executores
 */
async function carregarChartExecutores() {
    const limit = document.getElementById('selectLimitExecutores').value;
    const queryString = montarQueryString() + `&limit=${limit}`;
    
    const response = await fetch(`/dashboard/api/executores?${queryString}`);
    const result = await response.json();
    
    if (result.success) {
        const data = result.data;
        
        // Prepara dados
        const categorias = data.map(item => item.executor);
        const valores = data.map(item => item.total);
        
        // Destroi gráfico anterior
        if (charts.executores) {
            charts.executores.destroy();
        }
        
        // Opções do gráfico
        const options = {
            series: [{
                name: 'Tarefas Finalizadas',
                data: valores
            }],
            chart: {
                type: 'bar',
                height: 400
            },
            plotOptions: {
                bar: {
                    borderRadius: 4,
                    horizontal: true,
                    dataLabels: {
                        position: 'top'
                    }
                }
            },
            dataLabels: {
                enabled: true,
                offsetX: 30,
                style: {
                    fontSize: '12px',
                    colors: ['#304758']
                }
            },
            xaxis: {
                categories: categorias
            },
            colors: ['#28a745'],
            tooltip: {
                y: {
                    formatter: function(val) {
                        return val + ' tarefas';
                    }
                }
            }
        };
        
        charts.executores = new ApexCharts(document.querySelector('#chartExecutores'), options);
        charts.executores.render();
    }
}

/**
 * Carrega gráfico de locais
 */
async function carregarChartLocais() {
    const limit = document.getElementById('selectLimitLocais').value;
    const queryString = montarQueryString() + `&limit=${limit}`;
    
    const response = await fetch(`/dashboard/api/locais?${queryString}`);
    const result = await response.json();
    
    if (result.success) {
        const data = result.data;
        
        // Prepara dados
        const categorias = data.map(item => item.local);
        const valores = data.map(item => item.total);
        
        // Destroi gráfico anterior
        if (charts.locais) {
            charts.locais.destroy();
        }
        
        // Opções do gráfico
        const options = {
            series: [{
                name: 'Total de Tarefas',
                data: valores
            }],
            chart: {
                type: 'bar',
                height: 400
            },
            plotOptions: {
                bar: {
                    borderRadius: 4,
                    horizontal: true,
                    dataLabels: {
                        position: 'top'
                    }
                }
            },
            dataLabels: {
                enabled: true,
                offsetX: 30,
                style: {
                    fontSize: '12px',
                    colors: ['#304758']
                }
            },
            xaxis: {
                categories: categorias
            },
            colors: ['#17a2b8'],
            tooltip: {
                y: {
                    formatter: function(val) {
                        return val + ' tarefas';
                    }
                }
            }
        };
        
        charts.locais = new ApexCharts(document.querySelector('#chartLocais'), options);
        charts.locais.render();
    }
}

