// Toggle switches e confirmações
document.addEventListener('DOMContentLoaded', function() {
    // Confirmação de deleção
    const deleteButtons = document.querySelectorAll('.btn-danger');
    deleteButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            if (!confirm('Tem certeza que deseja deletar?')) {
                e.preventDefault();
            }
        });
    });
});
