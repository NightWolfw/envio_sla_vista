// Variáveis globais
let linhaCount = 0;

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
        const checkboxes = document.querySelectorAll('.grupo-checkbox');
        checkboxes.forEach(cb => cb.checked = this.checked);
    });

    // Adiciona primeira linha automaticamente
    adicionarLinha();
});

// Adicionar linha de agendamento
function adicionarLinha() {
    linhaCount++;
    const tbody = document.getElementById('linhasAgendamento');

    const row = document.createElement('tr');
    row.id = `linha-${linhaCount}`;
    row.innerHTML = `
        <td>
            <input type="datetime-local" class="form-control" id="data_envio_${linhaCount}" required>
        </td>
        <td>
            <input type="time" class="form-control" id="hora_inicio_${linhaCount}" required>
        </td>
        <td>
            <input type="number" class="form-control" id="offset_inicio_${linhaCount}" value="0" min="-7" max="7">
            <small class="text-muted">-1=ontem, 0=hoje, 1=amanhã</small>
        </td>
        <td>
            <input type="time" class="form-control" id="hora_fim_${linhaCount}" required>
        </td>
        <td>
            <input type="number" class="form-control" id="offset_fim_${linhaCount}" value="0" min="-7" max="7">
            <small class="text-muted">-1=ontem, 0=hoje, 1=amanhã</small>
        </td>
        <td>
            <button class="btn btn-sm btn-danger" onclick="removerLinha(${linhaCount})">🗑️</button>
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
// Aplicar limite de itens na tabela
function aplicarLimiteTabela() {
    const limite = parseInt(document.getElementById('limiteItens').value);
    const linhas = document.querySelectorAll('#tabelaGrupos tbody tr');
    let count = 0;

    linhas.forEach(linha => {
        if (linha.style.display !== 'none') {
            count++;
            if (count > limite) {
                linha.classList.add('hidden-by-limit');
                linha.style.display = 'none';
            } else {
                linha.classList.remove('hidden-by-limit');
                if (!linha.classList.contains('filtered-out')) {
                    linha.style.display = '';
                }
            }
        }
    });
}

// Atualizar aplicarFiltros para considerar o limite
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

        if (mostrar) {
            linha.classList.remove('filtered-out');
        } else {
            linha.classList.add('filtered-out');
        }

        linha.style.display = mostrar ? '' : 'none';
    });

    aplicarLimiteTabela();
}
