function getCookie(name) {
    let cookieValue = null;

    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');

        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();

            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }

    return cookieValue;
}


document.addEventListener('DOMContentLoaded', function () {
    const columns = document.querySelectorAll('.kanban-column');

    columns.forEach(function (column) {
        new Sortable(column, {
            group: 'kanban',
            animation: 150,
            ghostClass: 'bg-light',

            onAdd: function (event) {
                const taskCard = event.item;
                const newStatus = event.to.dataset.status;

                updateTaskStatus(taskCard, newStatus);
                updateEmptyColumnTexts();
            }
        });
    });

    updateEmptyColumnTexts();
});


function updateTaskStatus(taskCard, newStatus) {
    const csrftoken = getCookie('csrftoken');
    const updateUrl = taskCard.dataset.updateUrl;

    fetch(updateUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            status: newStatus
        })
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Ошибка ответа сервера');
            }

            return response.json();
        })
        .then(data => {
            if (!data.success) {
                alert('Ошибка при обновлении статуса задачи.');
                location.reload();
            }
        })
        .catch(error => {
            alert('Ошибка соединения с сервером.');
            location.reload();
        });
}


function updateEmptyColumnTexts() {
    const columns = document.querySelectorAll('.kanban-column');

    columns.forEach(function (column) {
        const tasks = column.querySelectorAll('.kanban-task');
        const emptyText = column.querySelector('.empty-column-text');

        if (tasks.length === 0) {
            if (!emptyText) {
                const p = document.createElement('p');
                p.className = 'text-muted small empty-column-text';
                p.innerText = 'Нет задач';
                column.appendChild(p);
            }
        } else {
            if (emptyText) {
                emptyText.remove();
            }
        }
    });
}