document.addEventListener('DOMContentLoaded', function() {
    const path = window.location.pathname;
    console.log(path);

    if (window.location.href.includes('/wedding/edit/')) { 
        $(document).ready(function () {
            const urlParts = window.location.pathname.split('/');
            const weddingID = urlParts[urlParts.length - 1]; 

            if (weddingID) {
                fetchWeddingDetails(weddingID);
            }
        });
        
        function fetchWeddingDetails(id) {
            $.ajax({
                url: `/wedding/${id}`,
                type: 'GET',
                success: function (data) {
                    console.log('/n/nFetched Data:', data);
                    fillEditForm(data); 
                },
                error: function (xhr, status, error) {
                    console.error('Error fetching wedding details:', error);
                }
            });
        }
        
        function fillEditForm(rowData) {
            $('#editButtonWedd').attr('data-id', rowData.id);
            $('#editid').val(rowData.id);
            
            $('#editGroomclient_id').val(rowData.groom_client_id);
            $('#editGroomFname').val(rowData.groom_fname);
            $('#editGroomMname').val(rowData.groom_mname);
            $('#editGroomLname').val(rowData.groom_lname);
            $('#editGroomBday').val(formatDate(rowData.groom_bday));
            $('#editGroomBplace').val(rowData.groom_bplace);
            $('#editGroomAddress').val(rowData.groom_address);
            $('#editGroomStatus').val(rowData.groom_status);
        
            $('#editGroomMoFname').val(rowData.groomMoFname);
            $('#editGroomMoMname').val(rowData.groomMoMname);
            $('#editGroomMoLname').val(rowData.groomMoLame);
            $('#editGroomMoBday').val(formatDate(rowData.groomMoBday));
            $('#editGroomMoBplace').val(rowData.groomMoBplace);
            $('#editGroomMoAddress').val(rowData.groomMoAddress);
        
            $('#editGroomFaFname').val(rowData.groomFaFname);
            $('#editGroomFaMname').val(rowData.groomFaMname);
            $('#editGroomFaLname').val(rowData.groomFaLname);
            $('#editGroomFaBday').val(formatDate(rowData.groomFaBday));
            $('#editGroomFaBplace').val(rowData.groomFaBplace);
            $('#editGroomFaAddress').val(rowData.groomFaAddress);




            $('#editBrideclient_id').val(rowData.bride_client_id);
            $('#editBrideFname').val(rowData.bride_fname);
            $('#editBrideMname').val(rowData.bride_mname);
            $('#editBrideLname').val(rowData.bride_lname);
            $('#editBrideBday').val(formatDate(rowData.bride_bday));
            $('#editBrideBplace').val(rowData.bride_bplace);
            $('#editBrideAddress').val(rowData.bride_address);
            $('#editBrideStatus').val(rowData.bride_status);
        
            $('#editBrideMoFname').val(rowData.brideMoFname);
            $('#editBrideMoMname').val(rowData.brideMoMname);
            $('#editBrideMoLname').val(rowData.brideMoLame);
            $('#editBrideMoBday').val(formatDate(rowData.brideMoBday));
            $('#editBrideMoBplace').val(rowData.brideMoBplace);
            $('#editBrideMoAddress').val(rowData.brideMoAddress);
        
            $('#editBrideFaFname').val(rowData.brideFaFname);
            $('#editBrideFaMname').val(rowData.brideFaMname);
            $('#editBrideFaLname').val(rowData.brideFaLname);
            $('#editBrideFaBday').val(formatDate(rowData.brideFaBday));
            $('#editBrideFaBplace').val(rowData.brideFaBplace);
            $('#editBrideFaAddress').val(rowData.brideFaAddress);
        
            $('#editWeddingDate').val(formatDate(rowData.wedding_date));
            $('#editpriest').val(rowData.priest_id);
        
            $('#editsponsorA').val(rowData.sponsorA);
            $('#editsponsorB').val(rowData.sponsorB);

            $('#editLicenseNum').val(rowData.license_number);
            $('#editCivilDate').val(formatDate(rowData.civil_date));
            $('#editCivilPlace').val(rowData.civil_place);
        
            // Set the value of ligitivity radio buttons
            if (rowData.groom_ligitivity === 'civil') {
                $('#GroomligitivityCivil').prop('checked', true);
            } else if (rowData.ligitivity === 'catholic') {
                $('#GroomligitivityCatholic').prop('checked', true);
            }

            if (rowData.bride_ligitivity === 'civil') {
                $('#BrideligitivityCivil').prop('checked', true);
            } else if (rowData.ligitivity === 'catholic') {
                $('#BrideligitivityCatholic').prop('checked', true);
            }
        }
    }

    document.body.addEventListener('click', function(event) {
        if (event.target.matches('button[data-page="insertWedd"]')) {
            event.preventDefault(); // Prevent the default form submission
            const form = document.querySelector('#insertWeddForm');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            console.log(data);
            print('BUTTON WAS PRESSED');
            insertWedding(data);
        } else if (event.target.matches('button[data-page="editWedd"]')) {
            event.preventDefault();
            const id = event.target.getAttribute('data-id');
            const form = document.getElementById('updateWeddForm');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            data['wedding_id'] = id; 
            console.log(data);
            editWedding(data);
        } else if (event.target.matches('button[data-page="deleteWedd"]')) {
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
                    deleteWedding(id);
                } else if (result.dismiss === Swal.DismissReason.cancel) {
                    console.log('Delete action was cancelled'); // Debugging
                } else {
                    console.log('Unexpected case:', result); // Debugging fallback
                }
            });
        }
    });
});

async function insertWedding(data) {
    try {
        const response = await fetch('/wedding/insert', {
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
            window.location.href = '/wedding';
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

async function editWedding(data) {
    alert('edit bapt pressed')
    try {
        const response = await fetch('/wedding/update', {
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
            window.location.href = '/wedding';
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

async function deleteWedding(id) {
    try {
        console.log(`Sending DELETE request for id: ${id}`); // Debugging log
        const response = await fetch(`/wedding/delete/${id}`, {
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
            window.location.href = '/wedding';
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