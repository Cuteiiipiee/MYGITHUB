<?php
require 'db.php';

// Check if the ID is passed
if (isset($_GET['id'])) {
    $task_id = $_GET['id'];

    // Delete the task from the database
    $stmt = $db->prepare("DELETE FROM tasks WHERE id = :id");
    $stmt->execute(['id' => $task_id]);

    // Redirect to the index page after deleting
    header("Location: index.php");
    exit;
} else {
    // If ID is not passed, redirect to index
    header("Location: index.php");
    exit;
}
?>

*update/replace your index.php code with this*
<?php
require 'db.php';

$tasks = $db->query("SELECT * FROM tasks ORDER BY created_at DESC")->fetchAll();
?>

           