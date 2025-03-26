document.addEventListener('DOMContentLoaded', function() {
    const path = window.location.pathname;
    console.log(path);

    document.body.addEventListener('click', function(event) {
        if (event.target.matches('button[data-page="insertPriest"]')) {
            event.preventDefault(); // Prevent the default form submission
            const form = document.querySelector('#insertPriestForm');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            console.log(data);
            console.log('BUTTON WAS PRESSED');
            insertPriest(data);
        } else if (event.target.matches('button[data-page="editPriest"]')) {
            event.preventDefault();
            const id = event.target.getAttribute('data-id');
            const form = document.getElementById('updatePriestForm');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            console.log(data);
            editPriest(data);
        } else if (event.target.matches('button[data-page="deletePriest"]')) {
            console.log('Attaching delete event listener'); // Debugging log
            event.preventDefault();
            const id = event.target.getAttribute('data-id');
            console.log(`Delete button clicked for id: ${id}`); // Debugging log
            
            Swal.fire({
                title: 'Are you sure?',
                text: "You won't be able to revert this!",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Yes, delete it!'
            }).then((result) => {
                console.log('Result:', result); // Debugging
                if (result.isConfirmed) {
                    console.log(`Confirmed delete for id: ${id}`); // Debugging
                    deletePriest(id);
                } else if (result.dismiss === Swal.DismissReason.cancel) {
                    console.log('Delete action was cancelled'); // Debugging
                } else {
                    console.log('Unexpected case:', result); // Debugging fallback
                }
            });
        }
    });
});

async function insertPriest(data) {
    try {
        const response = await fetch('/priest/insert', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`Error: ${response.statusText}`);
        }

        const result = await response.json();
        Swal.fire({
            title: 'Success!',
            text: result.message,
            icon: 'success',
            confirmButtonText: 'OK'
        }).then(() => {
            window.location.href = '/priest';
        });
    } catch (error) {
        console.error('Error inserting data:', error);
        Swal.fire({
            title: 'Error!',
            text: 'Failed to insert data.',
            icon: 'error',
            confirmButtonText: 'OK'
        });
    }
}

async function editPriest(data) {
    alert('edit priest pressed')
    try {
        const response = await fetch('/priest/update', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`Error: ${response.statusText}`);
        }

        const result = await response.json();
        Swal.fire({
            title: 'Success!',
            text: 'Your data has been updated.',
            icon: 'success',
            confirmButtonText: 'OK'
        }).then(() => {
            window.location.href = '/priest';
        });
    } catch (error) {
        console.error('Error updating data:', error);
        Swal.fire({
            title: 'Error!',
            text: 'Failed to update data.',
            icon: 'error',
            confirmButtonText: 'OK'
        });
    }
}

async function deletePriest(id) {
    try {
        console.log(`Sending DELETE request for id: ${id}`); // Debugging log
        const response = await fetch(`/priest/delete/${id}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            const result = await response.json();
            throw new Error(result.message);
        }

        const result = await response.json();
        Swal.fire({
            title: 'Deleted!',
            text: 'Your data has been deleted.',
            icon: 'success',
            confirmButtonText: 'OK'
        }).then(() => {
            window.location.href = '/priest';
        });
    } catch (error) {
        console.error('Error deleting data:', error);
        Swal.fire({
            title: 'Error!',
            text: 'Failed to delete data.',
            icon: 'error',
            confirmButtonText: 'OK'
        });
    }
}
