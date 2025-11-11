// Funções específicas para mensagens agendadas

// Toggle ativo/inativo via AJAX
function toggleMensagemAtiva(mensagemId) {
    fetch(`/mensagens/toggle/${mensagemId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const badge = document.querySelector(`#mensagem-${mensagemId} .badge-status`);
            if (data.ativo) {
                badge.className = 'badge badge-status bg-success';
                badge.textContent = 'Ativa';
            } else {
                badge.className = 'badge badge-status bg-secondary';
                badge.textContent = 'Inativa';
            }
            showToast('Status atualizado!', 'success');
        } else {
            showToast('Erro ao atualizar', 'error');
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        showToast('Erro na requisição', 'error');
    });
}

// Controle de tipo de recorrência
document.addEventListener('DOMContentLoaded', function() {
    const tipoRecorrencia = document.getElementById('tipo_recorrencia');
    const diasSemanaContainer = document.getElementById('dias_semana_container');
    const dataFimContainer = document.getElementById('data_fim_container');

    if (tipoRecorrencia) {
        tipoRecorrencia.addEventListener('change', function() {
            if (this.value === 'RECORRENTE') {
                diasSemanaContainer.style.display = 'block';
                dataFimContainer.style.display = 'block';
            } else {
                diasSemanaContainer.style.display = 'none';
                dataFimContainer.style.display = 'none';
            }
        });

        // Trigger inicial
        tipoRecorrencia.dispatchEvent(new Event('change'));
    }
});

// Seleção de grupos (marcar todos)
function marcarTodosGrupos(checkbox) {
    const checkboxes = document.querySelectorAll('input[name="grupos"]');
    checkboxes.forEach(cb => {
        if (cb.value !== 'todos') {
            cb.checked = checkbox.checked;
        }
    });
}

// Preview da mensagem
function previewMensagem() {
    const mensagem = document.getElementById('mensagem').value;
    const previewDiv = document.getElementById('preview_mensagem');

    if (previewDiv) {
        previewDiv.innerHTML = `
            <div class="alert alert-info">
                <strong>Preview:</strong><br>
                ${mensagem.replace(/\n/g, '<br>')}
            </div>
        `;
    }
}

// Validação do formulário
function validarFormularioMensagem(form) {
    const mensagem = form.querySelector('#mensagem').value.trim();
    const gruposSelecionados = form.querySelectorAll('input[name="grupos"]:checked');
    const horario = form.querySelector('#horario').value;
    const dataInicio = form.querySelector('#data_inicio').value;

    if (!mensagem) {
        showToast('Digite a mensagem', 'error');
        return false;
    }

    if (gruposSelecionados.length === 0) {
        showToast('Selecione pelo menos um grupo', 'error');
        return false;
    }

    if (!horario) {
        showToast('Selecione o horário', 'error');
        return false;
    }

    if (!dataInicio) {
        showToast('Selecione a data de início', 'error');
        return false;
    }

    return true;
}

// Helper toast
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();

    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'success' ? 'success' : 'danger'} border-0`;
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;

    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();

    toast.addEventListener('hidden.bs.toast', () => toast.remove());
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    document.body.appendChild(container);
    return container;
}
