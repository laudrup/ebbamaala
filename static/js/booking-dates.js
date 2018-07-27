$(function() {
  start_date = $('#id_start_date').datepicker();
  end_date = $('#id_end_date').datepicker();

  date_format = start_date.datepicker('option', 'dateFormat');
  console.assert(date_format === end_date.datepicker('option', 'dateFormat'),
                 'Start date and end date has different formats');

  start_date.datepicker('option', 'minDate', new Date());
  end_date.datepicker('option', 'minDate', new Date());

  start_date.on('change', function() {
    end_date.datepicker('option', 'minDate', get_date(this));
  });

  end_date.on('change', function() {
    start_date.datepicker('option', 'maxDate', get_date(this));
  });

  function get_date(element) {
    try {
      return $.datepicker.parseDate(date_format, element.value);
    } catch(error) {
      console.log('Error parsing date: ' + error)
      return null;
    }
  }
});
