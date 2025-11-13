// Variáveis globais
let linhaCount = 0;
let paginaAtual = 1;

// Mostrar loading
function showLoading() {
    document.getElementById('loadingOverlay').style.display = 'flex';
}

// Esconder loading
function hideLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
}

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    // Select all checkbox
    document.getElementById('selectAll').addEventListener('change', function() {
        // Seleciona apenas checkboxes visíveis (não filtrados/não ocultos)
        const checkboxes = document.querySelectorAll('.grupo-checkbox');
        checkboxes.forEach(cb => {
            const tr = cb.closest('tr');
            // Só marca se a linha estiver visível
            if (tr.style.display !== 'none') {
                cb.checked = this.checked;
            }
        });
    });

    // Adiciona primeira linha automaticamente
    adicionarLinha();
    
    // Aplica limite padrão ao carregar
    setTimeout(() => {
        aplicarLimiteTabela();
        atualizarTotalVisivel();
    }, 100);
});

// Adicionar linha de agendamento
function adicionarLinha() {
    linhaCount++;
    const tbody = document.getElementById('linhasAgendamento');

    const row = document.createElement('tr');
    row.id = `linha-${linhaCount}`;
    row.innerHTML = `
        <td>
            <input type="datetime-local" class="form-control form-control-sm" id="data_envio_${linhaCount}" required>
        </td>
        <td>
            <input type="time" class="form-control form-control-sm" id="hora_inicio_${linhaCount}" required>
        </td>
        <td>
            <input type="number" class="form-control form-control-sm" id="offset_inicio_${linhaCount}" value="0" min="-7" max="7" style="width: 80px; display: inline-block;">
            <small class="text-muted d-block">-1=ontem, 0=hoje, 1=amanhã</small>
        </td>
        <td>
            <input type="time" class="form-control form-control-sm" id="hora_fim_${linhaCount}" required>
        </td>
        <td>
            <input type="number" class="form-control form-control-sm" id="offset_fim_${linhaCount}" value="0" min="-7" max="7" style="width: 80px; display: inline-block;">
            <small class="text-muted d-block">-1=ontem, 0=hoje, 1=amanhã</small>
        </td>
        <td class="text-center">
            <button class="btn btn-sm btn-danger" onclick="removerLinha(${linhaCount})">
                <i class="bi bi-trash"></i>
            </button>
        </td>
    `;

    tbody.appendChild(row);
}

// Remover linha de agendamento
function removerLinha(id) {
    const linha = document.getElementById(`linha-${id}`);
    if (linha) {
        linha.remove();
    }
}

// Aplicar filtros na tabela
function aplicarFiltros() {
    const filtros = {
        diretor_executivo: document.getElementById('filtro_diretor_executivo').value,
        diretor_regional: document.getElementById('filtro_diretor_regional').value,
        gerente_regional: document.getElementById('filtro_gerente_regional').value,
        gerente: document.getElementById('filtro_gerente').value,
        supervisor: document.getElementById('filtro_supervisor').value,
        cliente: document.getElementById('filtro_cliente').value,
        pec_01: document.getElementById('filtro_pec_01').value,
        pec_02: document.getElementById('filtro_pec_02').value
    };

    const linhas = document.querySelectorAll('#tabelaGrupos tbody tr');

    linhas.forEach(linha => {
        let mostrar = true;

        Object.keys(filtros).forEach(campo => {
            if (filtros[campo] !== '') {
                const valorLinha = linha.getAttribute(`data-${campo.replace('_', '-')}`);
                if (valorLinha !== filtros[campo]) {
                    mostrar = false;
                }
            }
        });

        linha.style.display = mostrar ? '' : 'none';
    });
}

// Limpar filtros
function limparFiltros() {
    document.querySelectorAll('#filtrosAvancados select').forEach(select => {
        select.value = '';
    });
    aplicarFiltros();
}

// Mostrar preview da mensagem
function mostrarPreview(grupoId) {
    // Valida se tem pelo menos uma linha de agendamento
    const primeiraLinha = document.querySelector('#linhasAgendamento tr');
    if (!primeiraLinha) {
        alert('Adicione pelo menos um horário de envio!');
        return;
    }

    // Pega dados da primeira linha
    const dataEnvio = document.getElementById('data_envio_1').value;
    const horaInicio = document.getElementById('hora_inicio_1').value;
    const offsetInicio = document.getElementById('offset_inicio_1').value;
    const horaFim = document.getElementById('hora_fim_1').value;
    const offsetFim = document.getElementById('offset_fim_1').value;
    const tipoEnvio = document.querySelector('input[name="tipo_envio"]:checked').value;

    if (!dataEnvio || !horaInicio || !horaFim) {
        alert('Preencha os campos de data e horários!');
        return;
    }

    showLoading();

    // Faz requisição para preview
    const params = new URLSearchParams({
        tipo_envio: tipoEnvio,
        data_envio: dataEnvio,
        hora_inicio: horaInicio,
        dia_offset_inicio: offsetInicio,
        hora_fim: horaFim,
        dia_offset_fim: offsetFim
    });

    fetch(`/sla/preview/${grupoId}?${params}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('conteudoPreview').textContent = data.mensagem;
            const modal = new bootstrap.Modal(document.getElementById('modalPreview'));
            modal.show();
        })
        .catch(error => {
            alert('Erro ao carregar preview: ' + error);
        })
        .finally(() => {
            hideLoading();
        });
}

// Salvar agendamento
function salvarAgendamento() {
    // Pega grupos selecionados
    const gruposSelecionados = Array.from(document.querySelectorAll('.grupo-checkbox:checked'))
        .map(cb => parseInt(cb.value));

    if (gruposSelecionados.length === 0) {
        alert('Selecione pelo menos um grupo!');
        return;
    }

    // Pega dias da semana
    const diasSemana = Array.from(document.querySelectorAll('input[id^="dia_"]:checked'))
        .map(cb => cb.value);

    if (diasSemana.length === 0) {
        alert('Selecione pelo menos um dia da semana!');
        return;
    }

    // Pega tipo de envio
    const tipoEnvio = document.querySelector('input[name="tipo_envio"]:checked').value;

    // Pega todas as linhas de agendamento
    const linhas = document.querySelectorAll('#linhasAgendamento tr');
    const agendamentos = [];

    linhas.forEach((linha, index) => {
        const num = index + 1;
        const dataEnvio = document.getElementById(`data_envio_${num}`)?.value;
        const horaInicio = document.getElementById(`hora_inicio_${num}`)?.value;
        const offsetInicio = document.getElementById(`offset_inicio_${num}`)?.value;
        const horaFim = document.getElementById(`hora_fim_${num}`)?.value;
        const offsetFim = document.getElementById(`offset_fim_${num}`)?.value;

        if (dataEnvio && horaInicio && horaFim) {
            agendamentos.push({
                data_envio: dataEnvio,
                hora_inicio: horaInicio,
                dia_offset_inicio: offsetInicio,
                hora_fim: horaFim,
                dia_offset_fim: offsetFim
            });
        }
    });

    if (agendamentos.length === 0) {
        alert('Preencha pelo menos um agendamento completo!');
        return;
    }

    showLoading();

    // Para cada agendamento, salva para todos os grupos
    const promises = agendamentos.map(agendamento => {
        const dados = {
            grupos_ids: gruposSelecionados,
            tipo_envio: tipoEnvio,
            dias_semana: diasSemana,
            ...agendamento
        };

        return fetch('/sla/agendar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dados)
        });
    });

    Promise.all(promises)
        .then(responses => Promise.all(responses.map(r => r.json())))
        .then(results => {
            alert('Agendamentos criados com sucesso!');
            window.location.reload();
        })
        .catch(error => {
            alert('Erro ao salvar: ' + error);
        })
        .finally(() => {
            hideLoading();
        });
}
// Aplicar limite de itens na tabela com paginação
function aplicarLimiteTabela() {
    const limite = parseInt(document.getElementById('limiteItens').value);
    const linhas = document.querySelectorAll('#tabelaGrupos tbody tr');
    
    // Filtra apenas linhas visíveis (não filtradas)
    const linhasVisiveis = Array.from(linhas).filter(linha => 
        !linha.classList.contains('filtered-out')
    );
    
    const totalItens = linhasVisiveis.length;
    const totalPaginas = Math.ceil(totalItens / limite);
    
    // Ajusta página atual se necessário
    if (paginaAtual > totalPaginas) {
        paginaAtual = Math.max(1, totalPaginas);
    }
    
    const inicio = (paginaAtual - 1) * limite;
    const fim = inicio + limite;
    
    // Oculta todas as linhas primeiro
    linhas.forEach(linha => {
        linha.classList.remove('hidden-by-limit');
        if (linha.classList.contains('filtered-out')) {
            linha.style.display = 'none';
        }
    });
    
    // Mostra apenas as linhas da página atual
    linhasVisiveis.forEach((linha, index) => {
        if (index >= inicio && index < fim) {
            linha.style.display = '';
        } else {
            linha.classList.add('hidden-by-limit');
            linha.style.display = 'none';
        }
    });
    
    // Atualiza controles de paginação
    atualizarPaginacao(totalItens, totalPaginas, inicio, fim);
}

// Atualizar controles de paginação
function atualizarPaginacao(totalItens, totalPaginas, inicio, fim) {
    const paginacaoEl = document.getElementById('paginacao');
    const infoEl = document.getElementById('infoPaginacao');
    
    // Atualiza informação
    const mostrandoInicio = totalItens > 0 ? inicio + 1 : 0;
    const mostrandoFim = Math.min(fim, totalItens);
    infoEl.textContent = `Mostrando ${mostrandoInicio}-${mostrandoFim} de ${totalItens} grupos`;
    
    // Limpa paginação existente
    paginacaoEl.innerHTML = '';
    
    if (totalPaginas <= 1) {
        return; // Não precisa de paginação
    }
    
    // Botão "Anterior"
    const btnAnterior = document.createElement('li');
    btnAnterior.className = `page-item ${paginaAtual === 1 ? 'disabled' : ''}`;
    btnAnterior.innerHTML = `<a class="page-link" href="#" onclick="irParaPagina(${paginaAtual - 1}); return false;">Anterior</a>`;
    paginacaoEl.appendChild(btnAnterior);
    
    // Botões de página
    const maxBotoes = 5;
    let inicioPaginas = Math.max(1, paginaAtual - Math.floor(maxBotoes / 2));
    let fimPaginas = Math.min(totalPaginas, inicioPaginas + maxBotoes - 1);
    
    // Ajusta se estiver no final
    if (fimPaginas - inicioPaginas < maxBotoes - 1) {
        inicioPaginas = Math.max(1, fimPaginas - maxBotoes + 1);
    }
    
    // Primeira página
    if (inicioPaginas > 1) {
        const btn = document.createElement('li');
        btn.className = 'page-item';
        btn.innerHTML = `<a class="page-link" href="#" onclick="irParaPagina(1); return false;">1</a>`;
        paginacaoEl.appendChild(btn);
        
        if (inicioPaginas > 2) {
            const ellipsis = document.createElement('li');
            ellipsis.className = 'page-item disabled';
            ellipsis.innerHTML = `<span class="page-link">...</span>`;
            paginacaoEl.appendChild(ellipsis);
        }
    }
    
    // Páginas do meio
    for (let i = inicioPaginas; i <= fimPaginas; i++) {
        const btn = document.createElement('li');
        btn.className = `page-item ${i === paginaAtual ? 'active' : ''}`;
        btn.innerHTML = `<a class="page-link" href="#" onclick="irParaPagina(${i}); return false;">${i}</a>`;
        paginacaoEl.appendChild(btn);
    }
    
    // Última página
    if (fimPaginas < totalPaginas) {
        if (fimPaginas < totalPaginas - 1) {
            const ellipsis = document.createElement('li');
            ellipsis.className = 'page-item disabled';
            ellipsis.innerHTML = `<span class="page-link">...</span>`;
            paginacaoEl.appendChild(ellipsis);
        }
        
        const btn = document.createElement('li');
        btn.className = 'page-item';
        btn.innerHTML = `<a class="page-link" href="#" onclick="irParaPagina(${totalPaginas}); return false;">${totalPaginas}</a>`;
        paginacaoEl.appendChild(btn);
    }
    
    // Botão "Próximo"
    const btnProximo = document.createElement('li');
    btnProximo.className = `page-item ${paginaAtual === totalPaginas ? 'disabled' : ''}`;
    btnProximo.innerHTML = `<a class="page-link" href="#" onclick="irParaPagina(${paginaAtual + 1}); return false;">Próximo</a>`;
    paginacaoEl.appendChild(btnProximo);
}

// Ir para uma página específica
function irParaPagina(pagina) {
    paginaAtual = pagina;
    aplicarLimiteTabela();
}

// Mudar limite de itens por página
function mudarLimite() {
    paginaAtual = 1; // Volta para primeira página ao mudar limite
    aplicarLimiteTabela();
}

// Verificar filtros avançados para uma linha
function verificarFiltrosAvancados(linha) {
    const filtros = {
        diretor_executivo: document.getElementById('filtro_diretor_executivo')?.value || '',
        diretor_regional: document.getElementById('filtro_diretor_regional')?.value || '',
        gerente_regional: document.getElementById('filtro_gerente_regional')?.value || '',
        gerente: document.getElementById('filtro_gerente')?.value || '',
        supervisor: document.getElementById('filtro_supervisor')?.value || '',
        cliente: document.getElementById('filtro_cliente')?.value || '',
        pec_01: document.getElementById('filtro_pec_01')?.value || '',
        pec_02: document.getElementById('filtro_pec_02')?.value || ''
    };

    let passa = true;
    Object.keys(filtros).forEach(campo => {
        if (filtros[campo] !== '') {
            const valorLinha = linha.getAttribute(`data-${campo.replace('_', '-')}`);
            if (valorLinha !== filtros[campo]) {
                passa = false;
            }
        }
    });

    return passa;
}

// Filtro por texto (Nome, CR)
function aplicarFiltrosTexto() {
    const filtroNome = document.getElementById('filtro_nome')?.value.toLowerCase() || '';
    const filtroCr = document.getElementById('filtro_cr')?.value.toLowerCase() || '';
    
    const linhas = document.querySelectorAll('#tabelaGrupos tbody tr');
    
    linhas.forEach(linha => {
        const nome = (linha.getAttribute('data-nome') || '').toLowerCase();
        const cr = (linha.getAttribute('data-cr') || '').toLowerCase();
        
        const matchNome = !filtroNome || nome.includes(filtroNome);
        const matchCr = !filtroCr || cr.includes(filtroCr);
        
        // Verifica também os filtros avançados existentes
        const filtrosAvancados = verificarFiltrosAvancados(linha);
        
        if (matchNome && matchCr && filtrosAvancados) {
            linha.classList.remove('filtered-out');
            linha.style.display = '';
        } else {
            linha.classList.add('filtered-out');
            linha.style.display = 'none';
        }
    });
    
    // Reset para primeira página ao filtrar
    paginaAtual = 1;
    aplicarLimiteTabela();
    atualizarTotalVisivel();
}

// Atualizar total de grupos visíveis
function atualizarTotalVisivel() {
    const linhasVisiveis = document.querySelectorAll('#tabelaGrupos tbody tr:not(.filtered-out)');
    const total = linhasVisiveis.length;
    const totalElement = document.getElementById('totalGrupos');
    if (totalElement) {
        totalElement.textContent = total;
    }
}

// Atualizar aplicarFiltros para considerar o limite e filtros de texto
function aplicarFiltros() {
    // Usa a mesma lógica do filtro de texto
    aplicarFiltrosTexto();
}
