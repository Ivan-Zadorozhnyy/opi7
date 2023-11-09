document.addEventListener('DOMContentLoaded', (event) => {
  console.log('DOM fully loaded and parsed');

  // Example API call, replace `<report_name>`, `date_from` and `date_to` with your actual values.
  fetch('/api/report/<report_name>?from=2023-01-01&to=2023-01-31')
    .then(response => response.json())
    .then(data => {
      console.log(data);
      // Handle the data and insert it into the report div
      const reportDiv = document.getElementById('report');
      // Example of how you might render the data
      reportDiv.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
    })
    .catch(error => {
      console.error('Error fetching report:', error);
    });
});
