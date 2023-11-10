document.addEventListener('DOMContentLoaded', (event) => {
  console.log('DOM fully loaded and parsed');


  const reportName = 'report1';

  fetch(`/api/report/${reportName}?from=2023-01-01&to=2023-01-31`)
    .then(response => response.json())
    .then(data => {
      console.log(data);
      const reportDiv = document.getElementById('report');
      reportDiv.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
    })
    .catch(error => {
      console.error('Error fetching report:', error);
    });
});
