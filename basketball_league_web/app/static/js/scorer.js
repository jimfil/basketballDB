document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('event-modal');
    const closeBtn = document.querySelector('.close-btn');
    const playerBtns = document.querySelectorAll('.player-btn');
    const eventTypeBtns = document.querySelectorAll('.event-type-btn');
    const modalPlayerName = document.getElementById('modal-player-name');
    const modalPlayerId = document.getElementById('modal-player-id');

    playerBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const playerId = btn.dataset.playerId;
            const playerName = btn.textContent;
            modalPlayerId.value = playerId;
            modalPlayerName.textContent = playerName;
            modal.style.display = 'block';
        });
    });

    closeBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });

    eventTypeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const eventType = btn.dataset.eventType;
            const playerId = modalPlayerId.value;

            const payload = {
                match_id: MATCH_ID, // This should be defined in the HTML template
                player_id: parseInt(playerId),
                event_type: eventType
            };

            fetch('/api/event/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log('Event added:', data);
                    modal.style.display = 'none';
                } else {
                    console.error('Error adding event:', data.error);
                }
            })
            .catch(error => {
                console.error('Fetch error:', error);
            });
        });
    });
});
