#!/usr/bin/env node

const {execSync} = require("child_process");
const fs = require("fs");

const CHART_VALUES_FILENAME = "values.yaml";
const CHART_README_FILENAME = "README.md";
const CHART_VALUES_SCHEMA_FILENAME = "values.schema.json";
const README_GENERATOR_CMD = "npx readme-generator";

function getChangedFiles() {
    return execSync("git diff --cached --name-only --diff-filter=ACMR", {encoding: "utf-8"})
        .trim()
        .split("\n");
}

function getChangedFolders(changedFiles) {
    return [
        ...new Set(
            changedFiles
                .map((file) => file.split("/").slice(0, -1).join("/"))
                .filter((folder) => folder.length > 0)
        ),
    ];
}

function isChartFolder(folder) {
    return (
        fs.existsSync(`${folder}/${CHART_VALUES_FILENAME}`) &&
        fs.existsSync(`${folder}/${CHART_README_FILENAME}`)
    );
}

function runCommand(cmd, args, errorMessage) {
    try {
        execSync(`${cmd} ${args}`, {encoding: "utf-8", stdio: "pipe"});
    } catch (error) {
        console.error(`❌ ${errorMessage}`);
        console.error(error.stderr);
        console.error(error.stdout);
        process.exit(1);
    }
}

function updateChartDependencies(folder) {
    console.log(`🔄 Chart ${folder}: Updating dependencies`);
    const cmd = "helm";
    const args = `dependency update ${folder}`;
    const errorMessage = `Error running Helm Dependency Update for chart folder ${folder}`;
    runCommand(cmd, args, errorMessage);
}

function generateChartReadmeAndSchema(folder) {
    console.log(`📝 Chart ${folder}: Generating readme and schema`);
    const cmd = README_GENERATOR_CMD;
    const args = `-v "${folder}/${CHART_VALUES_FILENAME}" -r "${folder}/${CHART_README_FILENAME}" -s "${folder}/${CHART_VALUES_SCHEMA_FILENAME}"`;
    const errorMessage = `Error running Readme Generator for chart folder ${folder}`;
    runCommand(cmd, args, errorMessage);
}

function lintChartFolder(folder) {
    console.log(`🧐 Chart ${folder}: Running Helm Lint`);
    const cmd = "helm";
    const args = `lint ${folder}`;
    const errorMessage = `Error running Helm Lint for chart folder ${folder}`;
    runCommand(cmd, args, errorMessage);
}

function main() {
    console.log(`🔍 Check if changed folders are charts\n`);
    const changedFiles = getChangedFiles();
    const changedFolders = getChangedFolders(changedFiles);
    for (const folder of changedFolders) {
        if (isChartFolder(folder)) {
            updateChartDependencies(folder);
            generateChartReadmeAndSchema(folder);
            lintChartFolder(folder);
        } else {
            console.log(`🤷 Not a chart: ${folder}`);
        }
    }
    console.log(`\n⏱️ Script duration: ${process.uptime()} seconds`);
    console.log("\x1b[33m%s\x1b[0m", `\n💛 Stay Frank!`);
}

main();
