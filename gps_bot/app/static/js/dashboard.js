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
let filtrosAtivos = {};

// Variáveis de auto-refresh
let autoRefreshInterval = null;
let autoRefreshEnabled = true;
let ultimaAtualizacao = null;
const INTERVALO_ATUALIZACAO = 120000; // 2 minutos em ms

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    inicializarSelectMes();
    inicializarEventos();
    carregarDashboard();
    iniciarAutoRefresh();
});

/**
 * Inicializa select de mês
 */
function inicializarSelectMes() {
    const select = document.getElementById('selectMes');
    const meses = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ];
    
    const anoAtualTemp = new Date().getFullYear();
    
    // Adiciona meses do ano atual e anterior
    for (let ano = anoAtualTemp; ano >= anoAtualTemp - 1; ano--) {
        for (let mes = 12; mes >= 1; mes--) {
            const option = document.createElement('option');
            option.value = `${mes}-${ano}`;
            option.text = `${meses[mes - 1]}/${ano}`;
            
            if (mes === mesAtual && ano === anoAtual) {
                option.selected = true;
            }
            
            select.appendChild(option);
        }
    }
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
}

/**
 * Aplica filtros
 */
function aplicarFiltros() {
    const form = document.getElementById('formFiltros');
    const formData = new FormData(form);
    
    filtrosAtivos = {};
    for (let [key, value] of formData.entries()) {
        if (value) {
            filtrosAtivos[key] = value;
        }
    }
    
    carregarDashboard();
}

/**
 * Limpa filtros
 */
function limparFiltros() {
    document.getElementById('formFiltros').reset();
    filtrosAtivos = {};
    carregarDashboard();
}

/**
 * Monta query string com filtros
 */
function montarQueryString() {
    const params = new URLSearchParams();
    params.append('mes', mesAtual);
    params.append('ano', anoAtual);
    
    for (let [key, value] of Object.entries(filtrosAtivos)) {
        params.append(key, value);
    }
    
    return params.toString();
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
 */
function iniciarAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
    
    autoRefreshInterval = setInterval(function() {
        if (autoRefreshEnabled) {
            console.log('Auto-refresh: atualizando dashboard...');
            carregarDashboard();
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
    
    if (autoRefreshEnabled) {
        badge.className = 'badge bg-success status-ativo';
        badge.textContent = '🟢 Atualizando a cada 2min';
    } else {
        badge.className = 'badge bg-danger';
        badge.textContent = '🔴 Atualização Pausada';
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
 * Carrega gráfico de colunas
 */
async function carregarChartColunas() {
    const queryString = montarQueryString();
    
    const response = await fetch(`/dashboard/api/tarefas-mes?${queryString}`);
    const result = await response.json();
    
    if (result.success) {
        const data = result.data;
        
        // Prepara dados
        const categorias = data.map(item => {
            const date = new Date(item.dia);
            return date.getDate();
        });
        const valores = data.map(item => item.total);
        
        // Destroi gráfico anterior se existir
        if (charts.colunas) {
            charts.colunas.destroy();
        }
        
        // Opções do gráfico
        const options = {
            series: [{
                name: 'Tarefas',
                data: valores
            }],
            chart: {
                type: 'bar',
                height: 350,
                toolbar: {
                    show: true
                }
            },
            plotOptions: {
                bar: {
                    borderRadius: 4,
                    dataLabels: {
                        position: 'top'
                    }
                }
            },
            dataLabels: {
                enabled: true,
                offsetY: -20,
                style: {
                    fontSize: '12px',
                    colors: ['#304758']
                }
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
            colors: ['#0d6efd'],
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
 * Carrega heatmap
 */
async function carregarHeatmap() {
    const queryString = montarQueryString();
    
    const response = await fetch(`/dashboard/api/heatmap?${queryString}`);
    const result = await response.json();
    
    if (result.success) {
        const data = result.data;
        const tbody = document.getElementById('heatmapBody');
        tbody.innerHTML = '';
        
        if (data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center">Nenhum dado encontrado</td></tr>';
            return;
        }
        
        data.forEach(item => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${item.cr}</strong></td>
                <td>${item.contrato}</td>
                <td>${item.finalizadas}</td>
                <td>${item.total}</td>
                <td><strong>${item.porcentagem.toFixed(2)}%</strong></td>
                <td>
                    <span class="badge" style="background-color: ${item.cor_hex}; min-width: 80px;">
                        ${item.cor === 'verde' ? '✅ Ótimo' : item.cor === 'amarelo' ? '⚠️ Regular' : '❌ Crítico'}
                    </span>
                </td>
            `;
            tbody.appendChild(tr);
        });
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

