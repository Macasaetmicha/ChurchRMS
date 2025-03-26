document.addEventListener('DOMContentLoaded', function() {
    const path = window.location.pathname;
    console.log(path);

    if (window.location.href.includes('/baptism/edit/')) { 
        $(document).ready(function () {
            // Extract the baptism ID from the URL
            const urlParts = window.location.pathname.split('/');
            const baptismID = urlParts[urlParts.length - 1]; // Get the last part of the URL

            if (baptismID) {
                fetchBaptismDetails(baptismID);
            }
        });
        
        function fetchBaptismDetails(id) {
            $.ajax({
                url: `/baptism/${id}`,
                type: 'GET',
                success: function (data) {
                    console.log('/n/nFetched Data:', data);
                    fillEditForm(data); 
                },
                error: function (xhr, status, error) {
                    console.error('Error fetching baptism details:', error);
                }
            });
        }
        
        function fillEditForm(rowData) {
            $('#editButtonBapt').attr('data-id', rowData.id);
            $('#editid').val(rowData.id);
            $('#editclient_id').val(rowData.client_id);
            $('#editfname').val(rowData.fname);
            $('#editmname').val(rowData.mname);
            $('#editlname').val(rowData.lname);
            $('#editbirthday').val(formatDate(rowData.birthday));
            $('#editbirthplace').val(rowData.birthplace);
            $('#editaddress').val(rowData.address);
            $('#editstatus').val(rowData.status);
        
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
        
            $('#editbaptism_date').val(formatDate(rowData.baptism_date));
            $('#editpriest').val(rowData.priest_id);
        
            $('#editsponsorA').val(rowData.sponsorA);
            $('#editresidenceA').val(rowData.residenceA);
            $('#editsponsorB').val(rowData.sponsorB);
            $('#editresidenceB').val(rowData.residenceB);
        
            // Set the value of ligitivity radio buttons
            if (rowData.ligitivity === 'civil') {
                $('#ligitivityCivil').prop('checked', true);
            } else if (rowData.ligitivity === 'catholic') {
                $('#ligitivityCatholic').prop('checked', true);
            }
        }
    }

    document.body.addEventListener('click', function(event) {
        if (event.target.matches('button[data-page="insertBapt"]')) {
            event.preventDefault(); // Prevent the default form submission
            const form = document.querySelector('#insertBaptForm');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            console.log(data);
            console.log('BUTTON WAS PRESSED');
            insertBaptism(data);
        } else if (event.target.matches('button[data-page="editBapt"]')) {
            event.preventDefault();
            const id = event.target.getAttribute('data-id');
            const form = document.getElementById('updateBaptForm');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            data['baptism_id'] = id; 
            console.log(data);
            editBaptism(data);
        } else if (event.target.matches('button[data-page="deleteBapt"]')) {
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
                    deleteBaptism(id);
                } else if (result.dismiss === Swal.DismissReason.cancel) {
                    console.log('Delete action was cancelled'); // Debugging
                } else {
                    console.log('Unexpected case:', result); // Debugging fallback
                }
            });
        }
    });
});

async function insertBaptism(data) {
    try {
        const response = await fetch('/baptism/insert', {
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
            window.location.href = '/baptism';
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

async function editBaptism(data) {
    alert('edit bapt pressed')
    try {
        const response = await fetch('/baptism/update', {
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
            window.location.href = '/baptism';
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

async function deleteBaptism(id) {
    try {
        console.log(`Sending DELETE request for id: ${id}`); // Debugging log
        const response = await fetch(`/baptism/delete/${id}`, {
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
            window.location.href = '/baptism';
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

// document.addEventListener('DOMContentLoaded', function () {
//     console.log('DOM fully loaded and parsed'); // Debugging log
//     // Attach event listeners to insert buttons
//     document.querySelectorAll('.insert-btn-bapt').forEach(button => {
//         console.log('Add Button Pressed')
//         button.addEventListener('click', function (event) {
//             event.preventDefault(); // Prevent the default form submission
//             const form = document.querySelector('#insertBaptForm');
//             const formData = new FormData(form);
//             const data = Object.fromEntries(formData.entries());
//             console.log(data);
//             insertBaptism(data);
//         });
//     });

//     // Attach event listeners to edit buttons
//     document.querySelectorAll('.edit-btn-bapt').forEach(button => {
//         console.log('Edit Button pressed')
//         button.addEventListener('click', function (event) {
//             event.preventDefault();
//             const id = this.getAttribute('data-id');
//             const form = document.getElementById('updateBaptForm');
//             const formData = new FormData(form);
//             const data = Object.fromEntries(formData.entries());
//             data['baptism_id'] = id; 
//             console.log(data);
//             editBaptism(data);
//         });
//     });

//     // Attach event listeners to delete buttons
//     document.body.addEventListener('click', function (event) {
//         if (event.target.classList.contains('delete-btn-bapt')) {
//             console.log('Attaching delete event listener'); // Debugging log
//             event.preventDefault();
//             const id = event.target.getAttribute('data-id');
//             console.log(`Delete button clicked for id: ${id}`); // Debugging log
            
//             Swal.fire({
//                 title: 'Are you sure?',
//                 text: "You won't be able to revert this!",
//                 icon: 'warning',
//                 showCancelButton: true,
//                 confirmButtonColor: '#3085d6',
//                 cancelButtonColor: '#d33',
//                 confirmButtonText: 'Yes, delete it!'
//             }).then((result) => {
//                 console.log('Result:', result); // Debugging
//                 if (result.isConfirmed) {
//                     console.log(`Confirmed delete for id: ${id}`); // Debugging
//                     deleteBaptism(id);
//                 } else if (result.dismiss === Swal.DismissReason.cancel) {
//                     console.log('Delete action was cancelled'); // Debugging
//                 } else {
//                     console.log('Unexpected case:', result); // Debugging fallback
//                 }
//             });
//         }
//     });
// });

// async function insertBaptism(data) {
//     try {
//         const response = await fetch('/baptism/insert', {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json'
//             },
//             body: JSON.stringify(data)
//         });

//         if (!response.ok) {
//             throw new Error(`Error: ${response.statusText}`);
//         }

//         const result = await response.json();
//         Swal.fire({
//             title: 'Success!',
//             text: result.message,
//             icon: 'success',
//             confirmButtonText: 'OK'
//         }).then(() => {
//             window.location.href = '/baptism';
//         });
//     } catch (error) {
//         console.error('Error inserting data:', error);
//         Swal.fire({
//             title: 'Error!',
//             text: 'Failed to insert data.',
//             icon: 'error',
//             confirmButtonText: 'OK'
//         });
//     }
// }

// async function editBaptism(data) {
//     try {
//         const response = await fetch('/baptism/update', {
//             method: 'PUT',
//             headers: {
//                 'Content-Type': 'application/json'
//             },
//             body: JSON.stringify(data)
//         });

//         if (!response.ok) {
//             throw new Error(`Error: ${response.statusText}`);
//         }

//         const result = await response.json();
//         Swal.fire({
//             title: 'Success!',
//             text: 'Your data has been updated.',
//             icon: 'success',
//             confirmButtonText: 'OK'
//         }).then(() => {
//             window.location.href = '/baptism';
//         });
//     } catch (error) {
//         console.error('Error updating data:', error);
//         Swal.fire({
//             title: 'Error!',
//             text: 'Failed to update data.',
//             icon: 'error',
//             confirmButtonText: 'OK'
//         });
//     }
// }

// async function deleteBaptism(id) {
//     try {
//         console.log(`Sending DELETE request for id: ${id}`); // Debugging log
//         const response = await fetch(`/baptism/delete/${id}`, {
//             method: 'DELETE',
//             headers: {
//                 'Content-Type': 'application/json'
//             }
//         });

//         if (!response.ok) {
//             const result = await response.json();
//             throw new Error(result.message);
//         }

//         const result = await response.json();
//         Swal.fire({
//             title: 'Deleted!',
//             text: 'Your data has been deleted.',
//             icon: 'success',
//             confirmButtonText: 'OK'
//         }).then(() => {
//             window.location.href = '/baptism';
//         });
//     } catch (error) {
//         console.error('Error deleting data:', error);
//         Swal.fire({
//             title: 'Error!',
//             text: 'Failed to delete data.',
//             icon: 'error',
//             confirmButtonText: 'OK'
//         });
//     }
// }



