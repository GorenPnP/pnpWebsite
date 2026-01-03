function reset_filter() {
    document.querySelectorAll('.table-container tbody :where(input, select)').forEach(e => e.value=null);
    document.querySelector("#filter-form").submit();
}