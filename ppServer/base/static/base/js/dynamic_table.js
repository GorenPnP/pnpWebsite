function reset_filter() {
    document.querySelectorAll('.table-container tbody input').forEach(e => e.value=null);
    document.querySelector("#filter-form").submit();
}