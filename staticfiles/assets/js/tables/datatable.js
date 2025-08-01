$(document).ready(function () {	
	$('#example').DataTable();
	$('#example1').DataTable( {
        dom: 'Bfrtip',
        buttons: ['copy', 'csv', 'pdf', 'print']
    } );
	 $('#example2').DataTable( {
        "scrollY":        "500px",
        "scrollCollapse": true,
        "paging":         false,
		"bFilter": 		  false
    } );
});
