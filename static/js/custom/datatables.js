document.addEventListener('DOMContentLoaded', function () {
    const recordsTable = $('#recordsTable').DataTable({
        ajax: {
            url: '/records',
            dataSrc: ''
        },
        columns: [
            {
                data: null,
                render: function (data, type, row) {
                    return `
                        <button class="btn btn-primary find-btn" data-id="${row.id}">
                            <i class="fa-solid fa-info fa-fw"></i>
                        </button>
                    `;
                },
                orderable: false,
                searchable: false
            },
            { data: 'fname' },
            { data: 'mname' },
            { data: 'lname' },
            {
                data: 'birthday',
                render: function (data, type, row) {
                    return formatDateToLong(data);
                }
            },
            { data: 'ligitivity' },
            { data: 'birthplace' },
            { data: 'address' }
        ]
    });

    $('#recordsTable').on('click', '.find-btn', function () {
        const id = $(this).data('id');
        const rowData = recordsTable.row($(this).parents('tr')).data();
        // Populate the info modal with data
        $('#recClientName').text(`${rowData.fname} ${rowData.mname} ${rowData.lname}`);
        $('#recClientBday').text(formatDateToLong(rowData.birthday));
        $('#recClientBplace').text(rowData.birthplace);
        $('#recClientLigitivity').text(rowData.ligitivity);
        $('#recClientAddress').text(rowData.address);
        
        $('#recMoName').text(`${rowData.mother_fname} ${rowData.mother_mname} ${rowData.mother_lname}`);
        $('#recMoBday').text(formatDateToLong(rowData.mother_birthday));
        $('#recMoBplace').text(rowData.mother_bplace);
        $('#recMoAddress').text(rowData.mother_address);

        $('#recFaName').text(`${rowData.father_fname} ${rowData.father_mname} ${rowData.father_lname}`);
        $('#recFaBday').text(formatDateToLong(rowData.father_birthday));
        $('#recFaBplace').text(rowData.father_bplace);
        $('#recFaAddress').text(rowData.father_address);

        $('#deathIndex').text(rowData.death_index);
        $('#deathBook').text(rowData.death_book);
        $('#deathPage').text(rowData.death_page);
        $('#deathLine').text(rowData.death_line);
        $('#confIndex').text(rowData.conf_index);
        $('#confBook').text(rowData.conf_book);
        $('#confPage').text(rowData.conf_page);
        $('#confLine').text(rowData.conf_line);
        
        // Show the modal
        $('#modalsearch').modal('show');
    });


    const baptismTable = $('#baptismTable').DataTable({
        ajax: {
            url: '/baptism',
            dataSrc: '',
            data: function (d) {
                console.log('Data sent to the server for baptismTable:', d);
                // You can modify the data here if needed
                return d;
            }
        },
        columns: [
           {
                data: null,
                render: function (data, type, row) {
                    return `
                        <a href="/show/${row.id}" class="show-btn-bapt-trigger btn btn-primary btn-xs" data-toggle="modal" data-target="#baptShowModal" data-id="${row.id}">
                            <i class="fa-solid fa-info fa-fw"></i>
                        </a>
                        <a href="baptism/edit/${row.id}" class="mt-1 edit-btn-bapt-trigger btn btn-warning btn-xs" data-id="${row.id}">
                            <i class="fa-solid fa-edit fa-fw"></i>
                        </a>
                        <button class="mt-1 delete-btn-bapt btn btn-primary delete-btn" data-id="${row.id}" data-page="deleteBapt">
                            <i class="fa-solid fa-trash fa-fw"></i>
                        </button>`;
                },
                orderable: false,
                searchable: false
            },
            {
                data: 'baptism_date',
                render: function (data, type, row) {
                    return formatDateToLong(data);
                }
            },
            { data: 'fname' },
            { data: 'mname' },
            { data: 'lname' },
            {
                data: 'birthday',
                render: function (data, type, row) {
                    return formatDateToLong(data);
                }
            },
            { data: 'address' },
            {data: null,
                render: function (data, type, row) {
                    return `${row.father_fname} ${row.father_mname ? row.father_mname + ' ' : ''}${row.father_lname}`;
                }
            },
            {data: null,
                render: function (data, type, row) {
                    return `${row.mother_fname} ${row.mother_mname ? row.mother_mname + ' ' : ''}${row.mother_lname}`;
                }
            },
            { data: 'priest_name' }
        ], 
        initComplete: function (settings, json) {
            console.log('Data received from the server for baptismTable:', json);
        }
    });

    $('#baptismTable').on('click', '.show-btn-bapt-trigger', function () {
        const id = $(this).data('id'); // Get the ID from the button
    
        $.ajax({
            url: `/baptism/${id}`, // Fetch specific baptism record
            type: 'GET',
            dataType: 'json',
            success: function (rowData) {
                console.log('Fetched Baptism Data:', rowData);
                
                // Populate the info modal with the fetched data
                $('#baptClientName').text(`${rowData.fname} ${rowData.mname} ${rowData.lname}`);
                $('#baptClientBday').text(formatDateToLong(rowData.birthday));
                $('#baptClientBplace').text(rowData.birthplace);
                $('#baptClientLigitivity').text(rowData.ligitivity);
                $('#baptClientAddress').text(rowData.address);
                $('#baptClientStatus').text(rowData.status);
                
                $('#baptMoName').text(`${rowData.mother_fname} ${rowData.mother_mname} ${rowData.mother_lname}`);
                $('#baptMoBday').text(formatDateToLong(rowData.mother_birthday));
                $('#baptMoBplace').text(rowData.mother_bplace);
                $('#baptMoAddress').text(rowData.mother_address);
    
                $('#baptFaName').text(`${rowData.father_fname} ${rowData.father_mname} ${rowData.father_lname}`);
                $('#baptFaBday').text(formatDateToLong(rowData.father_birthday));
                $('#baptFaBplace').text(rowData.father_bplace);
                $('#baptFaAddress').text(rowData.father_address);
    
                $('#baptDate').text(formatDateToLong(rowData.baptism_date));
                $('#baptPriest').text(rowData.priest_name);
                $('#baptSponsA').text(rowData.sponsorA);
                $('#baptResiA').text(rowData.residenceA);
                $('#baptSponsB').text(rowData.sponsorB);
                $('#baptResiB').text(rowData.residenceB);
    
                $('#baptIndex').text(rowData.rec_index);
                $('#baptBook').text(rowData.rec_book);
                $('#baptPage').text(rowData.rec_page);
                $('#baptLine').text(rowData.rec_line);
    
                // Show the modal
                $('#baptShowModal').modal('show');
            },
            error: function (xhr, status, error) {
                console.error('Error fetching baptism record:', error);
                alert('Failed to load data. Please try again.');
            }
        });
    });

    const confirmationTable = $('#confirmationTable').DataTable({
        ajax: {
            url: '/confirmation',
            dataSrc: '',
            data: function (d) {
                console.log('Data sent to the server for confirmationTable:', d);
                // You can modify the data here if needed
                return d;
            }
        },
        columns: [
           {
                data: null,
                render: function (data, type, row) {
                    return `
                        <a href="/show/${row.id}" class="show-btn-conf-trigger btn btn-primary btn-xs" data-toggle="modal" data-target="#confShowModal" data-id="${row.id}">
                            <i class="fa-solid fa-info fa-fw"></i>
                        </a>
                        <a href="confirmation/edit/${row.id}" class="mt-1 edit-btn-conf-trigger btn btn-warning btn-xs" data-id="${row.id}">
                            <i class="fa-solid fa-edit fa-fw"></i>
                        </a>
                        <button class="mt-1 delete-btn-conf btn btn-primary" data-id="${row.id}" data-page="deleteConf">
                            <i class="fa-solid fa-trash fa-fw"></i>
                        </button>                    
                        `;
                },
                orderable: false,
                searchable: false
            },
            {
                data: 'confirmation_date',
                render: function (data, type, row) {
                    return formatDateToLong(data);
                }
            },
            { data: 'fname' },
            { data: 'mname' },
            { data: 'lname' },
            {
                data: 'birthday',
                render: function (data, type, row) {
                    return formatDateToLong(data);
                }
            },
            { data: 'address' },
            {data: null,
                render: function (data, type, row) {
                    return `${row.father_fname} ${row.father_mname ? row.father_mname + ' ' : ''}${row.father_lname}`;
                }
            },
            {data: null,
                render: function (data, type, row) {
                    return `${row.mother_fname} ${row.mother_mname ? row.mother_mname + ' ' : ''}${row.mother_lname}`;
                }
            },
            { data: 'priest_name' }
        ], 
        initComplete: function (settings, json) {
            console.log('Data received from the server for confirmationTable:', json);
        }
    });

    $('#confirmationTable').on('click', '.show-btn-conf-trigger', function () {
        const id = $(this).data('id'); // Get the ID from the button
    
        $.ajax({
            url: `/confirmation/${id}`, // Fetch specific baptism record
            type: 'GET',
            dataType: 'json',
            success: function (rowData) {
                console.log('Fetched Confirmation Data:', rowData);
                
                $('#confClientName').text(`${rowData.fname} ${rowData.mname} ${rowData.lname}`);
                $('#confClientBday').text(formatDateToLong(rowData.birthday));
                $('#confClientBplace').text(rowData.birthplace);
                $('#confClientLigitivity').text(rowData.ligitivity);
                $('#confClientAddress').text(rowData.address);
                $('#confChurchBapt').text(rowData.church_baptized);
                
                $('#confMoName').text(`${rowData.mother_fname} ${rowData.mother_mname} ${rowData.mother_lname}`);
                $('#confMoBday').text(formatDateToLong(rowData.mother_birthday));
                $('#confMoBplace').text(rowData.mother_bplace);
                $('#confMoAddress').text(rowData.mother_address);

                $('#confFaName').text(`${rowData.father_fname} ${rowData.father_mname} ${rowData.father_lname}`);
                $('#confFaBday').text(formatDateToLong(rowData.father_birthday));
                $('#confFaBplace').text(rowData.father_bplace);
                $('#confFaAddress').text(rowData.father_address);

                $('#confDate').text(formatDateToLong(rowData.confirmation_date));
                $('#confPriest').text(rowData.priest_name);
                $('#confSponsA').text(rowData.sponsorA);
                $('#confSponsB').text(rowData.sponsorB);

                $('#confIndex').text(rowData.rec_index);
                $('#confBook').text(rowData.rec_book);
                $('#confPage').text(rowData.rec_page);
                $('#confLine').text(rowData.rec_line);
    
                // Show the modal
                $('#confShowModal').modal('show');
            },
            error: function (xhr, status, error) {
                console.error('Error fetching Confirmation record:', error);
                alert('Failed to load data. Please try again.');
            }
        });
    });

    const weddingTable = $('#weddingTable').DataTable({
        ajax: {
            url: '/wedding',
            dataSrc: '',
            data: function (d) {
                console.log('Data sent to the server for weddingTable:', d);
                // You can modify the data here if needed
                return d;
            }
        },
        columns: [
           {
                data: null,
                render: function (data, type, row) {
                    return `
                        <a href="/show/${row.id}" class="show-btn-wedd-trigger btn btn-primary btn-xs" data-toggle="modal" data-target="#weddShowModal" data-id="${row.id}">
                            <i class="fa-solid fa-info fa-fw"></i>
                        </a>
                        <a href="wedding/edit/${row.id}" class="mt-1 edit-btn-wedd-trigger btn btn-warning btn-xs" data-id="${row.id}">
                            <i class="fa-solid fa-edit fa-fw"></i>
                        </a>
                        <button class="mt-1 delete-btn-wedd btn btn-primary" data-id="${row.id}" data-page="deleteWedd">
                            <i class="fa-solid fa-trash fa-fw"></i>
                        </button>                    
                        `;
                },
                orderable: false,
                searchable: false
            },
            {
                data: 'wedding_date',
                render: function (data, type, row) {
                    return formatDateToLong(data);
                }
            },
            { data: null,
                render: function (data, type, row) {
                    return `${row.groom_fname} ${row.groom_mname ? row.groom_mname + ' ' : ''}${row.groom_lname}`;
                }
            },
            { data: 'groom_bday',
                render: function (data, type, row) {
                    return calculateAge(data);
                }},
            { data: 'groom_status' },
            { data: 'groom_address' },
             { data: null,
                render: function (data, type, row) {
                    return `${row.bride_fname} ${row.bride_mname ? row.bride_mname + ' ' : ''}${row.bride_lname}`;
                }
            },
            { data: 'bride_bday',
                render: function (data, type, row) {
                    return calculateAge(data);
                } },
            { data: 'bride_status' },
            { data: 'bride_address' },
            { data: 'priest_name' }
        ], 
        initComplete: function (settings, json) {
            console.log('Data received from the server for confirmationTable:', json);
        }
    });

    $('#weddingTable').on('click', '.show-btn-wedd-trigger', function () {
        const id = $(this).data('id'); 
        console.log('This id the ID of the record:', id)
    
        $.ajax({
            url: `/wedding/${id}`, 
            type: 'GET',
            dataType: 'json',
            success: function (rowData) {
                console.log('Fetched Wedding Data:', rowData);
                
                $('#weddGroomName').text(`${rowData.groom_fname} ${rowData.groom_mname} ${rowData.groom_lname}`);
                $('#weddGroomBday').text(formatDateToLong(rowData.groom_bday));
                $('#weddGroomBplace').text(rowData.groom_bplace);
                $('#weddGroomLigitivity').text(rowData.groom_ligitivity);
                $('#weddGroomAddress').text(rowData.groom_address);
                $('#weddGroomStatus').text(rowData.groom_status);
                
                $('#weddGroomMoName').text(`${rowData.groomMoFname} ${rowData.groomMoMname} ${rowData.groomMoLname}`);
                $('#weddGroomMoBday').text(formatDateToLong(rowData.groomMoBday));
                $('#weddGroomMoBplace').text(rowData.groomMoBplace);
                $('#weddGroomMoAddress').text(rowData.groomMoAddress);

                $('#weddGroomFaName').text(`${rowData.groomFaFname} ${rowData.groomFaMname} ${rowData.groomFaLname}`);
                $('#weddGroomFaBday').text(formatDateToLong(rowData.groomFaBday));
                $('#weddGroomFaBplace').text(rowData.groomFaBplace);
                $('#weddGroomFaAddress').text(rowData.groomFaAddress);

                $('#weddBrideName').text(`${rowData.bride_fname} ${rowData.bride_mname} ${rowData.bride_lname}`);
                $('#weddBrideBday').text(formatDateToLong(rowData.bride_bday));
                $('#weddBrideBplace').text(rowData.bride_bplace);
                $('#weddBrideLigitivity').text(rowData.bride_ligitivity);
                $('#weddBrideAddress').text(rowData.bride_address);
                $('#weddBrideStatus').text(rowData.bride_status);
                
                $('#weddBrideMoName').text(`${rowData.brideMoFname} ${rowData.brideMoMname} ${rowData.brideMoLname}`);
                $('#weddBrideMoBday').text(formatDateToLong(rowData.brideMoBday));
                $('#weddBrideMoBplace').text(rowData.brideMoBplace);
                $('#weddBrideMoAddress').text(rowData.brideMoAddress);

                $('#weddBrideFaName').text(`${rowData.brideFaFname} ${rowData.brideFaMname} ${rowData.brideFaLname}`);
                $('#weddBrideFaBday').text(formatDateToLong(rowData.brideFaBday));
                $('#weddBrideFaBplace').text(rowData.brideFaBplace);
                $('#weddBrideFaAddress').text(rowData.brideFaAddress);

                $('#weddDate').text(formatDateToLong(rowData.wedding_date));
                $('#weddPriest').text(rowData.priest_name);
                $('#weddSponsA').text(rowData.sponsorA);
                $('#weddSponsB').text(rowData.sponsorB);

                $('#licenseNumber').text(rowData.license_number);
                $('#civilDate').text(formatDateToLong(rowData.civil_date));
                $('#civilPlace').text(rowData.civil_place);

                $('#weddIndex').text(rowData.rec_index);
                $('#weddBook').text(rowData.rec_book);
                $('#weddPage').text(rowData.rec_page);
                $('#weddLine').text(rowData.rec_line);
    
                // Show the modal
                $('#weddShowModal').modal('show');
            },
            error: function (xhr, status, error) {
                console.error('Error fetching Wedding record:', error);
                alert('Failed to load data. Please try again.');
            }
        });
    });

    const deathTable = $('#deathTable').DataTable({
        ajax: {
            url: '/death',
            dataSrc: '',
            data: function (d) {
                console.log('Data sent to the server for deathTable:', d);
                // You can modify the data here if needed
                return d;
            }
        },
        columns: [
           {
                data: null,
                render: function (data, type, row) {
                    return `
                        <a href="/show/${row.id}" class="show-btn-death-trigger btn btn-primary btn-xs" data-toggle="modal" data-target="#deathShowModal" data-id="${row.id}">
                            <i class="fa-solid fa-info fa-fw"></i>
                        </a>
                        <a href="death/edit/${row.id}" class="mt-1 edit-btn-death-trigger btn btn-warning btn-xs" data-id="${row.id}">
                            <i class="fa-solid fa-edit fa-fw"></i>
                        </a>
                        <button class="mt-1 delete-btn-death btn btn-primary" data-id="${row.id}" data-page="deleteDeath">
                            <i class="fa-solid fa-trash fa-fw"></i>
                        </button>                    
                        `;
                },
                orderable: false,
                searchable: false
            },
            {
                data: 'death_date',
                render: function (data, type, row) {
                    return formatDateToLong(data);
                }
            },
            {
                data: 'burial_date',
                render: function (data, type, row) {
                    return formatDateToLong(data);
                }
            },
            { data: 'fname' },
            { data: 'mname' },
            { data: 'lname' },
            {
                data: 'birthday',
                render: function (data, type, row) {
                    return formatDateToLong(data);
                }
            },
            { data: 'address' },
            {data: null,
                render: function (data, type, row) {
                    return `${row.father_fname} ${row.father_mname ? row.father_mname + ' ' : ''}${row.father_lname}`;
                }
            },
            {data: null,
                render: function (data, type, row) {
                    return `${row.mother_fname} ${row.mother_mname ? row.mother_mname + ' ' : ''}${row.mother_lname}`;
                }
            },
            { data: 'priest_name' }
        ], 
        initComplete: function (settings, json) {
            console.log('Data received from the server for deathTable:', json);
        }
    });

    $('#deathTable').on('click', '.show-btn-death-trigger', function () {
        const id = $(this).data('id'); 
        console.log('This id the ID of the record:', id)
    
        $.ajax({
            url: `/death/${id}`, // Fetch specific baptism record
            type: 'GET',
            dataType: 'json',
            success: function (rowData) {
                console.log('Fetched Death Data:', rowData);
                
                // Populate the info modal with the fetched data
                $('#deathClientName').text(`${rowData.fname} ${rowData.mname} ${rowData.lname}`);
                $('#deathClientBday').text(formatDateToLong(rowData.birthday));
                $('#deathClientBplace').text(rowData.birthplace);
                $('#deathClientLigitivity').text(rowData.ligitivity);
                $('#deathClientAddress').text(rowData.address);
                $('#deathClientStatus').text(rowData.status);
                
                $('#deathMoName').text(`${rowData.mother_fname} ${rowData.mother_mname} ${rowData.mother_lname}`);
                $('#deathMoBday').text(formatDateToLong(rowData.mother_birthday));
                $('#deathMoBplace').text(rowData.mother_bplace);
                $('#deathMoAddress').text(rowData.mother_address);
    
                $('#deathFaName').text(`${rowData.father_fname} ${rowData.father_mname} ${rowData.father_lname}`);
                $('#deathFaBday').text(formatDateToLong(rowData.father_birthday));
                $('#deathFaBplace').text(rowData.father_bplace);
                $('#deathFaAddress').text(rowData.father_address);
    
                $('#deathDate').text(formatDateToLong(rowData.death_date));
                $('#burialDate').text(formatDateToLong(rowData.burial_date));
                $('#burialPlace').text(rowData.burial_place);
                $('#deathCause').text(rowData.cause);
                $('#deathCP').text(rowData.contact_person);
                $('#deathCPAddress').text(rowData.cp_address);
                $('#deathPriest').text(rowData.priest_name);
    
                $('#deathIndex').text(rowData.rec_index);
                $('#deathBook').text(rowData.rec_book);
                $('#deathPage').text(rowData.rec_page);
                $('#deathLine').text(rowData.rec_line);
    
                // Show the modal
                $('#deathShowModal').modal('show');
            },
            error: function (xhr, status, error) {
                console.error('Error fetching death record:', error);
                alert('Failed to load data. Please try again.');
            }
        });
    });

    const priestTable = $('#priestTable').DataTable({
        ajax: {
            url: '/priest',
            dataSrc: ''
        },
        columns: [
            {
                data: null,
                render: function (data, type, row) {
                    return `
                        <a href="/show/${row.id}" class="show-btn-priest-trigger btn btn-primary btn-xs" data-toggle="modal" data-target="#priestShowModal" data-id="${row.id}">
                            <i class="fa-solid fa-info fa-fw"></i>
                        </a>
                        <a href="/priest/edit/${row.id}" class="edit-btn-priest-trigger btn btn-warning btn-xs" data-toggle="modal" data-target="#priestEditModal" data-id="${row.id}">
                            <i class="fa-solid fa-edit fa-fw"></i>
                        </a>
                        <button class="delete-btn-priest btn btn-primary" data-id="${row.id}" data-page="deletePriest">
                            <i class="fa-solid fa-trash fa-fw"></i>
                        </button>                    `;
                },
                orderable: false,
                searchable: false
            },
            { data: 'name' },
            { data: 'position' },
            { data: 'church' }
        ]
    });

    $('#priestTable').on('click', '.show-btn-priest-trigger', function () {
        console.log('Show button clicked');
        const id = $(this).data('id'); 
        console.log('This id the ID of the record:', id)
    
        $.ajax({
            url: `/priest/${id}`, // Fetch specific baptism record
            type: 'GET',
            dataType: 'json',
            success: function (rowData) {
                console.log('Fetched Death Data:', rowData);
                
                $('#priestName').text(rowData.name);
                $('#priestChurch').text(rowData.church);
                $('#priestPosition').text(rowData.position);
                $('#priestStatus').text(rowData.status);
    
                // Show the modal
                $('#priestShowModal').modal('show');
            },
            error: function (xhr, status, error) {
                console.error('Error fetching death record:', error);
                alert('Failed to load data. Please try again.');
            }
        });
    });

    $('#priestTable').on('click', '.edit-btn-priest-trigger', function () {
        console.log('Show button clicked');
        const id = $(this).data('id'); 
        console.log('This id the ID of the record:', id)
    
        $.ajax({
            url: `/priest/${id}`, // Fetch specific baptism record
            type: 'GET',
            dataType: 'json',
            success: function (rowData) {
                console.log('Fetched Death Data:', rowData);
                
                // Populate the form fields in the edit modal
                $('#editid').val(rowData.id); // Hidden field for ID
                $('#editPriestName').val(rowData.name);
                $('#editPriestChurch').val(rowData.church);
                $('#editPriestPosition').val(rowData.position);
                $('#editPriestStatus').val(rowData.status);

                // Show the modal
                $('#priestEditModal').modal('show');
            },
            error: function (xhr, status, error) {
                console.error('Error fetching priest record:', error);
                alert('Failed to load data. Please try again.');
            }
        });
    });

    


    // Function to format date to YYYY-MM-DD
    function formatDate(dateString) {
        const date = new Date(dateString);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    // Function to format date to "MM/DD/YYYY"
    function formatDateToMMDDYYYY(dateString) {
        const date = new Date(dateString);
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const year = date.getFullYear();
        return `${month}/${day}/${year}`;
    }

    // Function to format date to "Month DD, YYYY"
    function formatDateToLong(dateString) {
        const date = new Date(dateString);
        const options = { year: 'numeric', month: 'long', day: 'numeric' };
        return date.toLocaleDateString('en-US', options);
    }

    function calculateAge(birthday) {
        let birthDate = new Date(birthday);
        let today = new Date();

        let age = today.getFullYear() - birthDate.getFullYear();

        let monthDiff = today.getMonth() - birthDate.getMonth();
        let dayDiff = today.getDate() - birthDate.getDate();
    
        if (monthDiff < 0 || (monthDiff === 0 && dayDiff < 0)) {
            age--;
        }
        return age;
    }

    window.formatDate = formatDate;
    window.formatDateToLong = formatDateToLong;
});


