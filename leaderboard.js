async function fetchLeaderboard() {
    try {
        const response = await fetch('https://europe-west2-g3casino.cloudfunctions.net/user/affiliate/referral-leaderboard', {
            headers: {
                'Authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiI1a1V0ZzFPTWV0SzhvZkFvRTFteiIsImlhdCI6MTcyMzExMzQ3MH0.GpTH9ix0WrKeWOh7B__wQEwRrzzeaNZkUSMU4wamBiA'
            }
        });

        // Check if the request was successful
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        // Parse the JSON data
        const data = await response.json();

        // Validate the structure of the JSON response
        if (data.success && data.data && Array.isArray(data.data.players)) {
            return data;
        } else {
            throw new Error('Invalid JSON structure');
        }
    } catch (error) {
        console.error('Error fetching leaderboard:', error);
        return null;
    }
}

function displayLeaderboard(leaderboardData) {
    const leaderboardBody = document.getElementById('leaderboard-body');
    leaderboardBody.innerHTML = '';

    if (leaderboardData && leaderboardData.success) {
        const players = leaderboardData.data.players;
        players.forEach((player, index) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${index + 1}</td>
                <td>${player.username}</td>
                <td>${player.points}</td>
            `;
            leaderboardBody.appendChild(row);
        });
    } else {
        leaderboardBody.innerHTML = '<tr><td colspan="3">Failed to fetch the leaderboard.</td></tr>';
    }
}

async function updateLeaderboard() {
    const leaderboardData = await fetchLeaderboard();
    if (leaderboardData) {
        displayLeaderboard(leaderboardData);
    } else {
        document.getElementById('leaderboard-body').innerHTML = '<tr><td colspan="3">An error occurred while fetching the leaderboard.</td></tr>';
    }
}

// Update the leaderboard when the page loads
updateLeaderboard();

// Update the leaderboard every 5 minutes
setInterval(updateLeaderboard, 5 * 60 * 1000);
