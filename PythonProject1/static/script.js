async function castVote() {
    const voterId = document.getElementById('voterId').value.trim();
    const partySelect = document.getElementById('partySelect');
    const partyName = partySelect.options[partySelect.selectedIndex].text;
    const messageDiv = document.getElementById('message');

    messageDiv.textContent = '';
    messageDiv.className = '';

    if (!voterId) {
        showMessage('Please enter Voter ID', 'error');
        return;
    }
    if (partyName === 'Select Political Party') {
        showMessage('Please select a political party', 'error');
        return;
    }

    try {
        const response = await fetch('/vote', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                voter_id: voterId,
                party_name: partyName
            })
        });

        const result = await response.json();

        if (result.status === 'success') {
            showMessage('Vote recorded successfully!', 'success');
            document.getElementById('voterId').value = '';
            partySelect.selectedIndex = 0;
            await fetchResults();
        } else {
            showMessage(result.message || 'Vote submission failed', 'error');
        }
    } catch (error) {
        showMessage('Error submitting vote', 'error');
        console.error('Error:', error);
    }
}

function showMessage(text, type) {
    const messageDiv = document.getElementById('message');
    messageDiv.textContent = text;
    messageDiv.className = type;
}

async function fetchResults() {
    try {
        const response = await fetch('/results');
        const text = await response.text();
        const resultsContainer = document.getElementById('resultsContainer');
        resultsContainer.innerHTML = text;
    } catch (error) {
        console.error('Error fetching results:', error);
        const resultsContainer = document.getElementById('resultsContainer');
        resultsContainer.innerHTML = '<p>Unable to fetch results</p>';
    }
}

document.addEventListener('DOMContentLoaded', fetchResults);