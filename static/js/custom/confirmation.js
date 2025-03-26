document.addEventListener('DOMContentLoaded', function(){
    const path = window.location.pathname;
    console.log(path)

    if (window.location.href.includes('/confirmation/edit')) {
        $(document).ready(function () {
            const urlParts = window.location.pathname.split('/');
            const confirmationID = urlParts[urlParts.length -1];

            if (confirmationID) {
                fetchConfirmationDetails(confirmationID)
            }
        })

        function fetchConfirmationDetails(id) {
            $.ajax({
                url: `/confirmation/${id}`,
                type: `GET`,
                success: function(data) {
                    console.log('/n/nFetched Data:', data);
                    fillEditForm(data);
                }
            })
        }

        function fillEditForm(rowData){
            $('#editButtonBapt').attr('data-id', rowData.id);
            $('#editid').val(rowData.id);
            $('#editclient_id').val(rowData.client_id);
            $('#editfname').val(rowData.fname);
            $('#editmname').val(rowData.mname);
            $('#editlname').val(rowData.lname);
            $('#editbirthday').val(formatDate(rowData.birthday));
            $('#editbirthplace').val(rowData.birthplace);
            $('#editaddress').val(rowData.address);
            $('#editchurchbapt').val(rowData.church_baptized);
        
            $('#editmother_fname').val(rowData.mother_fname);
            $('#editmother_mname').val(rowData.mother_mname);
            $('#editmother_lname').val(rowData.mother_lname);
            $('#editmother_birthday').val(formatDate(rowData.mother_birthday));
            $('#editmother_bplace').val(rowData.mother_bplace);
            $('#editmother_address').val(rowData.mother_address);
        
            $('#editfather_fname').val(rowData.father_fname);
            $('#editfather_mname').val(rowData.father_mname);
            $('#editfather_lname').val(rowData.father_lname);
            $('#editfather_birthday').val(formatDate(rowData.father_birthday));
            $('#editfather_bplace').val(rowData.father_bplace);
            $('#editfather_address').val(rowData.father_address);
        
            $('#editconfirmation_date').val(formatDate(rowData.confirmation_date));
            $('#editpriest').val(rowData.priest_id);
        
            $('#editsponsorA').val(rowData.sponsorA);
            $('#editsponsorB').val(rowData.sponsorB);
        
            // Set the value of ligitivity radio buttons
            if (rowData.ligitivity === 'civil') {
                $('#ligitivityCivil').prop('checked', true);
            } else if (rowData.ligitivity === 'catholic') {
                $('#ligitivityCatholic').prop('checked', true);
            }
        }
    }

    document.body.addEventListener('click', function(event) {
        if (event.target.matches('button[data-page="insertConf"]')) {
            alert('button pressed')
            event.preventDefault(); // Prevent the default form submission
            const form = document.querySelector('#insertConfForm');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            console.log(data);
            alert('got details')
            insertConfirmation(data);
        } else if (event.target.matches('button[data-page="editConf"]')) {
            event.preventDefault();
            const id = event.target.getAttribute('data-id');
            const form = document.getElementById('updateConfForm');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            data['confirmation_id'] = id; 
            alert('UPDATE CONFIRMATION: ', data);
            editConfirmation(data);
        } else if (event.target.matches('button[data-page="deleteConf"]')) {
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
                    deleteConfirmation(id);
                } else if (result.dismiss === Swal.DismissReason.cancel) {
                    console.log('Delete action was cancelled'); // Debugging
                } else {
                    console.log('Unexpected case:', result); // Debugging fallback
                }
            });
        }
    });
})

async function insertConfirmation(data) {
    try {
        const response = await fetch('/confirmation/insert', {
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
            window.location.href = '/confirmation';
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

async function editConfirmation(data) {
    try {
        const response = await fetch('/confirmation/update', {
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
            window.location.href = '/confirmation';
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

async function deleteConfirmation(id) {
    try {
        console.log(`Sending DELETE request for id: ${id}`); // Debugging log
        const response = await fetch(`/confirmation/delete/${id}`, {
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
            window.location.href = '/confirmation';
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

