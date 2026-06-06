<?php

require_once('/usr/local/envs/php-twig-1.19/vendor/autoload.php');

class Blog {
    public $user;
    public $desc;
    private $twig;

    public function __construct($user, $desc) {
        $this->user = $user;
        $this->desc = $desc;
    }

    public function __toString() {
        return $this->twig->render('index', ['user' => $this->user]);
    }

    public function __wakeup() {
        $loader = new Twig_Loader_Array([
            'index' => $this->desc,
        ]);
        $this->twig = new Twig_Environment($loader);
    }

    public function __sleep() {
        return ["user", "desc"];
    }
}

?>