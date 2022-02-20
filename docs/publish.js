var ghpages = require('gh-pages');
var process = require('child_process')

process.exec(
    "poetry run python -c \"import crescent; print(crescent.__version__)\"",
    (err, stdout, stderr) => {
        if (stderr != 0) {
            commit_message = ":memo: publish docs"
        } else {
            commit_message = `:memo: publish docs for version ${stdout.trim()}`
        }

        console.log(commit_message)
        ghpages.publish(
            'docs/_build',
            {
                message: commit_message,
                user: {
                    name: "Github Actions",
                    email: "actions@magpie.dev",
                }
            },
            err => { }
        );

    }
)
