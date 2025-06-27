<script>
  let { data, children } = $props();

  data = data || {};

  import "../app.css";
</script>

{@render children()}