// Funções específicas para a página de grupos

// Toggle de envio via AJAX
function toggleEnvio(grupoId) {
    fetch(`/grupos/toggle_envio/${grupoId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const badge = document.querySelector(`#grupo-${grupoId} .badge`);
            if (data.novo_status) {
                badge.className = 'badge bg-success';
                badge.textContent = 'Ativo';
            } else {
                badge.className = 'badge bg-danger';
                badge.textContent = 'Inativo';
            }
            showToast('Status atualizado com sucesso!', 'success');
        } else {
            showToast('Erro ao atualizar status', 'error');
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        showToast('Erro na requisição', 'error');
    });
}

// Confirmação antes de deletar
document.addEventListener('DOMContentLoaded', function() {
    const deleteButtons = document.querySelectorAll('.btn-delete-grupo');

    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();

            const grupoNome = this.dataset.grupoNome;
            const form = this.closest('form');

            if (confirm(`Tem certeza que deseja deletar o grupo "${grupoNome}"?`)) {
                form.submit();
            }
        });
    });
});

// Filtros dinâmicos
function aplicarFiltros() {
    const filtroId = document.getElementById('filtro_id').value;
    const filtroNome = document.getElementById('filtro_nome').value;
    const filtroCr = document.getElementById('filtro_cr').value;

    const params = new URLSearchParams();
    if (filtroId) params.append('filtro_id', filtroId);
    if (filtroNome) params.append('filtro_nome', filtroNome);
    if (filtroCr) params.append('filtro_cr', filtroCr);

    window.location.href = `/grupos/?${params.toString()}`;
}

// Helper para toast notifications
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();

    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'success' ? 'success' : 'danger'} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;

    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();

    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    document.body.appendChild(container);
    return container;
}
