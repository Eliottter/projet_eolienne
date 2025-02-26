const { Octokit } = require("@octokit/rest");
const fs = require("fs");
const config = require("./config.json");

const octokit = new Octokit({ auth: config.authToken });

async function uploadFiles() {
    for (const filePath of config.filesToUpload) {
        const content = fs.readFileSync(filePath, { encoding: "base64" });
        const fileName = filePath.split("/").pop();

        await octokit.repos.createOrUpdateFileContents({
            owner: config.repository.split("/")[0],
            repo: config.repository.split("/")[1],
            path: fileName,
            message: config.commitMessage,
            content: content,
            branch: config.branch
        });

        console.log(`Fichier ${fileName} sauvegardé sur GitHub.`);
    }
}

uploadFiles().catch(console.error);
