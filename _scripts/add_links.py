#!/usr/bin/env python3
"""
Add clickable links to task items and resource pills across all 7 course trackers.
- Resources become <a> anchors with real URLs
- Key "Read / Take / Install" tasks get a small ↗ link icon
- Two helper functions renderTask/renderRes are added to each file
- CSS is updated so a.res-pill is styled as a link
"""
import json, re, os

BASE = '/home/ht/Documents/GitHub_HT/certified-journeys.github.io/courses'

# ── per-course URL mappings ────────────────────────────────────────────────────
COURSE_DATA = {

    'pspo-certified': {
        'resources': {
            'Scrum Guide PDF (scrumguides.org)':
                ('Scrum Guide 2020 PDF', 'https://scrumguides.org/docs/scrumguide/v2020/2020-Scrum-Guide-US.pdf'),
            'Scrum Guide audio (YouTube)':
                ('Scrum Guide 2020 – Audio', 'https://scrumguides.org/scrum-guide.html'),
            'PSPO Open Assessment (scrum.org/open-assessments)':
                ('PSPO Open Assessment', 'https://www.scrum.org/open-assessments'),
            'Scrum.org Learning Path':
                ('Scrum.org PSPO Learning Path', 'https://www.scrum.org/pathway/professional-scrum-product-owner-learning-path'),
            'Scrum Guide §Product Owner':
                ('Scrum Guide — Product Owner', 'https://scrumguides.org/scrum-guide.html#product-owner'),
            'Mikhail Lapshin quiz (mlapshin.com)':
                ('Mikhail Lapshin PSPO Quiz', 'https://mlapshin.com/index.php/scrum-quizzes/'),
            'Scrum.org open assessment':
                ('PSPO Open Assessment', 'https://www.scrum.org/open-assessments'),
            'Scrum.org PSPO competency areas':
                ('Scrum.org PSPO Competencies', 'https://www.scrum.org/professional-scrum-competencies'),
            'Mikhail Lapshin — stakeholder question set':
                ('Mikhail Lapshin PSPO Quiz', 'https://mlapshin.com/index.php/scrum-quizzes/'),
            'Scrum.org PSPO competencies':
                ('Scrum.org PSPO Competencies', 'https://www.scrum.org/professional-scrum-competencies'),
            'Scrum Guide §Sprint Review':
                ('Scrum Guide — Sprint Review', 'https://scrumguides.org/scrum-guide.html#sprint-review'),
            'Scrum Guide §Values':
                ('Scrum Guide — Scrum Values', 'https://scrumguides.org/scrum-guide.html#scrum-values'),
            'Scrum.org learning path — empiricism module':
                ('Scrum.org PSPO Learning Path', 'https://www.scrum.org/pathway/professional-scrum-product-owner-learning-path'),
            'Mikhail Lapshin Real Mode':
                ('Mikhail Lapshin PSPO Quiz', 'https://mlapshin.com/index.php/scrum-quizzes/'),
            'Scrum Guide (post-exam targeted review)':
                ('Scrum Guide 2020', 'https://scrumguides.org/scrum-guide.html'),
            'Scrum Guide (targeted)':
                ('Scrum Guide 2020', 'https://scrumguides.org/scrum-guide.html'),
            'Scrum.org PSPO Open Assessment':
                ('PSPO Open Assessment', 'https://www.scrum.org/open-assessments'),
            'PrepForScrum mock exam (prepforscrum.com)':
                ('PrepForScrum PSPO Practice Exam', 'https://www.prepforscrum.com/'),
            'scrum.org/assessments — exam booking page':
                ('Scrum.org — Book PSPO I Exam', 'https://www.scrum.org/assessments'),
            'Mikhail Lapshin learning mode':
                ('Mikhail Lapshin PSPO Quiz', 'https://mlapshin.com/index.php/scrum-quizzes/'),
            'Scrum Guide §Product Backlog':
                ('Scrum Guide — Product Backlog', 'https://scrumguides.org/scrum-guide.html#product-backlog'),
            'Scrum Guide §Events':
                ('Scrum Guide — Scrum Events', 'https://scrumguides.org/scrum-guide.html#scrum-events'),
            'Scrum Guide §Product Goal':
                ('Scrum Guide — Product Goal', 'https://scrumguides.org/scrum-guide.html#product-backlog'),
        },
        'task_links': [
            ('Read Scrum Guide 2020 cover to cover',
             'https://scrumguides.org/docs/scrumguide/v2020/2020-Scrum-Guide-US.pdf'),
            ('Re-read Scrum Guide focusing on artifacts',
             'https://scrumguides.org/scrum-guide.html#scrum-artifacts'),
            ('Take Scrum.org PSPO Open Assessment',
             'https://www.scrum.org/open-assessments'),
            ('Take Mikhail Lapshin PSPO quiz in Learning Mode',
             'https://mlapshin.com/index.php/scrum-quizzes/'),
            ('Take Mikhail Lapshin PSPO quiz in Real Mode',
             'https://mlapshin.com/index.php/scrum-quizzes/'),
            ('Take a second full 80-question timed mock',
             'https://www.prepforscrum.com/'),
            ('Retake Scrum.org PSPO Open Assessment',
             'https://www.scrum.org/open-assessments'),
            ('Book PSPO I exam at scrum.org',
             'https://www.scrum.org/assessments'),
        ],
    },

    'dlt-certified': {
        'resources': {
            'dlthub.com/docs/intro':
                ('dlt docs — Introduction', 'https://dlthub.com/docs/intro'),
            'dlt GitHub: github.com/dlt-hub/dlt':
                ('dlt GitHub Repository', 'https://github.com/dlt-hub/dlt'),
            'dlt REST API source docs':
                ('dlt REST API Source', 'https://dlthub.com/docs/dlt-ecosystem/verified-sources/rest_api'),
            'dlt verified sources (github.com/dlt-hub/verified-sources)':
                ('dlt Verified Sources', 'https://github.com/dlt-hub/verified-sources'),
            'dlt destinations docs':
                ('dlt Destinations', 'https://dlthub.com/docs/dlt-ecosystem/destinations'),
            'dlt DuckDB destination (fastest for local dev)':
                ('dlt DuckDB Destination', 'https://dlthub.com/docs/dlt-ecosystem/destinations/duckdb'),
            'dlt incremental loading docs':
                ('dlt Incremental Loading', 'https://dlthub.com/docs/general-usage/incremental-loading'),
            'dlt pipeline state docs':
                ('dlt Pipeline State', 'https://dlthub.com/docs/general-usage/state'),
            'dlt schema docs':
                ('dlt Schema', 'https://dlthub.com/docs/general-usage/schema'),
            'dlt data contracts guide':
                ('dlt Data Contracts', 'https://dlthub.com/docs/general-usage/schema-contracts'),
            'dlt dbt integration docs':
                ('dlt + dbt Integration', 'https://dlthub.com/docs/dlt-ecosystem/transformations/dbt'),
            'dlt + dbt example (GitHub)':
                ('dlt + dbt Example', 'https://github.com/dlt-hub/dlt/tree/devel/docs/examples'),
            'dlt error handling docs':
                ('dlt Error Handling', 'https://dlthub.com/docs/running-in-production/running'),
            'dlt Pydantic integration guide':
                ('dlt Pydantic Integration', 'https://dlthub.com/docs/general-usage/schema-contracts#pydantic-models'),
            'dlt deployment docs':
                ('dlt Deployment Guide', 'https://dlthub.com/docs/walkthroughs/deploy-a-pipeline'),
            'dlt Airflow integration example':
                ('dlt + Airflow', 'https://dlthub.com/docs/walkthroughs/deploy-a-pipeline/deploy-with-airflow-composer'),
            'dlt rest_api source helper docs':
                ('dlt REST API Source Helper', 'https://dlthub.com/docs/dlt-ecosystem/verified-sources/rest_api'),
            'dlt nested data normalization guide':
                ('dlt Nested Normalization', 'https://dlthub.com/docs/general-usage/schema#nested-data-normalization'),
            'dlt showcase gallery (dlthub.com/showcase)':
                ('dlt Showcase Gallery', 'https://dlthub.com/showcase'),
        },
        'task_links': [
            ('Read dlt docs: What is dlt?', 'https://dlthub.com/docs/intro'),
            ('Install dlt: pip install dlt', 'https://dlthub.com/docs/reference/installation'),
            ('Integrate dlt with dbt', 'https://dlthub.com/docs/dlt-ecosystem/transformations/dbt'),
            ('Deploy a dlt pipeline to GitHub Actions',
             'https://dlthub.com/docs/walkthroughs/deploy-a-pipeline/deploy-with-github-actions'),
        ],
    },

    'polars-certified': {
        'resources': {
            'docs.pola.rs/getting-started':
                ('Polars — Getting Started', 'https://docs.pola.rs/user-guide/getting-started/'),
            'Polars GitHub: github.com/pola-rs/polars':
                ('Polars GitHub', 'https://github.com/pola-rs/polars'),
            'Polars expressions docs':
                ('Polars Expressions', 'https://docs.pola.rs/user-guide/expressions/'),
            'Polars user guide — expressions chapter':
                ('Polars User Guide', 'https://docs.pola.rs/user-guide/'),
            'Polars lazy API docs':
                ('Polars Lazy API', 'https://docs.pola.rs/user-guide/lazy/'),
            'Polars query optimization guide':
                ('Polars Query Optimization', 'https://docs.pola.rs/user-guide/lazy/query-plan/'),
            'Polars groupby docs':
                ('Polars GroupBy', 'https://docs.pola.rs/user-guide/expressions/aggregation/'),
            'Polars window functions guide':
                ('Polars Window Functions', 'https://docs.pola.rs/user-guide/expressions/window/'),
            'Polars string namespace docs':
                ('Polars String Namespace', 'https://docs.pola.rs/user-guide/expressions/strings/'),
            'Polars datetime docs':
                ('Polars Datetime', 'https://docs.pola.rs/user-guide/expressions/temporal/'),
            'Polars joins docs':
                ('Polars Joins', 'https://docs.pola.rs/user-guide/transformations/joins/'),
            'Polars reshape guide':
                ('Polars Reshape', 'https://docs.pola.rs/user-guide/transformations/'),
            'Polars I/O docs':
                ('Polars I/O', 'https://docs.pola.rs/user-guide/io/'),
            'Polars + DuckDB integration guide':
                ('Polars + DuckDB', 'https://duckdb.org/docs/guides/python/polars'),
            'Polars performance guide':
                ('Polars Performance', 'https://docs.pola.rs/user-guide/misc/'),
            'Polars benchmarks (github.com/pola-rs)':
                ('Polars Benchmarks', 'https://github.com/pola-rs/tpch'),
            'Polars user-defined functions docs':
                ('Polars UDFs', 'https://docs.pola.rs/user-guide/expressions/plugins/'),
            'Polars plugin development guide':
                ('Polars Plugin Guide', 'https://docs.pola.rs/user-guide/expressions/plugins/'),
            'Polars example notebooks':
                ('Polars Example Notebooks', 'https://github.com/pola-rs/polars/tree/main/examples'),
        },
        'task_links': [
            ('Install Polars: pip install polars',
             'https://docs.pola.rs/user-guide/getting-started/'),
            ('Run the Polars quickstart',
             'https://docs.pola.rs/user-guide/getting-started/'),
        ],
    },

    'terraform-certified': {
        'resources': {
            'developer.hashicorp.com/terraform/tutorials':
                ('HashiCorp Terraform Tutorials', 'https://developer.hashicorp.com/terraform/tutorials'),
            'Terraform AWS provider docs':
                ('Terraform AWS Provider', 'https://registry.terraform.io/providers/hashicorp/aws/latest/docs'),
            'HashiCorp Learn: Get Started with AWS':
                ('HashiCorp — Get Started AWS', 'https://developer.hashicorp.com/terraform/tutorials/aws-get-started'),
            'Terraform resource docs':
                ('Terraform Resources', 'https://developer.hashicorp.com/terraform/language/resources'),
            'Terraform data sources guide':
                ('Terraform Data Sources', 'https://developer.hashicorp.com/terraform/language/data-sources'),
            'Terraform variables docs':
                ('Terraform Variables', 'https://developer.hashicorp.com/terraform/language/values/variables'),
            'HashiCorp variable precedence guide':
                ('Variable Precedence', 'https://developer.hashicorp.com/terraform/language/values/variables#variable-definition-precedence'),
            'Terraform state docs':
                ('Terraform State', 'https://developer.hashicorp.com/terraform/language/state'),
            'Terraform backend configuration guide':
                ('Terraform Backends', 'https://developer.hashicorp.com/terraform/language/settings/backends/configuration'),
            'Terraform module docs':
                ('Terraform Modules', 'https://developer.hashicorp.com/terraform/language/modules'),
            'Terraform Registry — official modules':
                ('Terraform Registry', 'https://registry.terraform.io/'),
            'Terraform built-in functions reference':
                ('Terraform Functions', 'https://developer.hashicorp.com/terraform/language/functions'),
            'HashiCorp Learn: expressions tutorial':
                ('HashiCorp Expressions Tutorial', 'https://developer.hashicorp.com/terraform/tutorials/configuration-language/expressions'),
            'Terraform Cloud docs':
                ('Terraform Cloud', 'https://developer.hashicorp.com/terraform/cloud-docs'),
            'HashiCorp Learn: Terraform Cloud tutorials':
                ('HashiCorp Terraform Cloud Tutorials', 'https://developer.hashicorp.com/terraform/tutorials/cloud'),
            'Terraform lifecycle docs':
                ('Terraform Lifecycle', 'https://developer.hashicorp.com/terraform/language/meta-arguments/lifecycle'),
            'Terraform provisioners guide':
                ('Terraform Provisioners', 'https://developer.hashicorp.com/terraform/language/resources/provisioners/syntax'),
            'Terraform workspace docs':
                ('Terraform Workspaces', 'https://developer.hashicorp.com/terraform/language/state/workspaces'),
            'HashiCorp workspace best practices':
                ('Workspace Best Practices', 'https://developer.hashicorp.com/terraform/cloud-docs/workspaces'),
            'Bryan Krausen Terraform practice exams (Udemy)':
                ('Bryan Krausen Terraform Udemy', 'https://www.udemy.com/user/bryan-krausen/'),
            'HashiCorp Study Guide':
                ('HashiCorp Terraform Study Guide', 'https://developer.hashicorp.com/terraform/tutorials/certification-003/associate-study-003'),
            'Terraform sensitive variable docs':
                ('Sensitive Variables', 'https://developer.hashicorp.com/terraform/language/values/variables#suppressing-values-in-cli-output'),
            'HashiCorp Vault + Terraform integration':
                ('Vault + Terraform', 'https://developer.hashicorp.com/terraform/tutorials/secrets/secrets-vault'),
            'HashiCorp certification portal':
                ('HashiCorp Certification Portal', 'https://developer.hashicorp.com/certifications/infrastructure-automation'),
            'Pearson VUE online proctoring':
                ('Pearson VUE', 'https://home.pearsonvue.com/'),
            'HashiCorp Terraform Associate study guide':
                ('Terraform Associate Study Guide', 'https://developer.hashicorp.com/terraform/tutorials/certification-003/associate-study-003'),
        },
        'task_links': [
            ('Install Terraform and verify:',
             'https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli'),
            ('Take a 57-question Terraform practice exam',
             'https://www.udemy.com/user/bryan-krausen/'),
            ('Book exam: $70 USD',
             'https://developer.hashicorp.com/certifications/infrastructure-automation'),
        ],
    },

    'aws-ml-certified': {
        'resources': {
            'AWS ML Specialty Exam Guide (aws.training)':
                ('AWS ML Specialty Exam Guide', 'https://aws.amazon.com/certification/certified-machine-learning-specialty/'),
            'A Cloud Guru or Udemy AWS ML course overview':
                ('A Cloud Guru AWS ML Course', 'https://acloudguru.com/course/aws-certified-machine-learning-specialty'),
            'AWS Glue docs':
                ('AWS Glue', 'https://docs.aws.amazon.com/glue/latest/dg/what-is-glue.html'),
            'Kinesis whitepaper':
                ('Amazon Kinesis', 'https://docs.aws.amazon.com/streams/latest/dev/introduction.html'),
            'A Cloud Guru lab: Data Engineering':
                ('A Cloud Guru', 'https://acloudguru.com/course/aws-certified-machine-learning-specialty'),
            'SageMaker Data Wrangler docs':
                ('SageMaker Data Wrangler', 'https://docs.aws.amazon.com/sagemaker/latest/dg/data-wrangler.html'),
            'AWS EDA whitepaper':
                ('AWS Analytics Whitepaper', 'https://docs.aws.amazon.com/whitepapers/latest/aws-overview/analytics.html'),
            'SageMaker Developer Guide':
                ('SageMaker Developer Guide', 'https://docs.aws.amazon.com/sagemaker/latest/dg/whatis.html'),
            'SageMaker immersion day labs':
                ('SageMaker Immersion Day', 'https://catalog.us-east-1.prod.workshops.aws/workshops/63069e26-921c-4ce1-9cc7-debb66a991ef'),
            'SageMaker built-in algorithms guide':
                ('SageMaker Built-in Algorithms', 'https://docs.aws.amazon.com/sagemaker/latest/dg/algos.html'),
            'AWS Deep Learning Containers docs':
                ('AWS DL Containers', 'https://docs.aws.amazon.com/deep-learning-containers/latest/devguide/what-is-dlc.html'),
            'SageMaker distributed training guide':
                ('SageMaker Distributed Training', 'https://docs.aws.amazon.com/sagemaker/latest/dg/distributed-training.html'),
            'Tutorials Dojo AWS ML Specialty practice exams':
                ('Tutorials Dojo AWS ML', 'https://tutorialsdojo.com/courses/aws-certified-machine-learning-specialty-practice-exams/'),
            'Whizlabs AWS ML practice tests':
                ('Whizlabs AWS ML', 'https://www.whizlabs.com/aws-certified-machine-learning-specialty/'),
            'SageMaker Hyperparameter Tuning docs':
                ('SageMaker HPO', 'https://docs.aws.amazon.com/sagemaker/latest/dg/automatic-model-tuning.html'),
            'AWS ML University — optimization module':
                ('AWS ML University', 'https://aws.amazon.com/machine-learning/mlu/'),
            'SageMaker Security Best Practices':
                ('SageMaker Security', 'https://docs.aws.amazon.com/sagemaker/latest/dg/security.html'),
            'AWS ML Governance whitepaper':
                ('AWS ML Governance', 'https://docs.aws.amazon.com/whitepapers/latest/ml-best-practices-healthcare-life-sciences/governance.html'),
            'SageMaker MLOps docs':
                ('SageMaker MLOps', 'https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-projects.html'),
            'AWS MLOps framework whitepaper':
                ('AWS MLOps Whitepaper', 'https://docs.aws.amazon.com/whitepapers/latest/mlops-principles/mlops-principles.html'),
            'AWS ML Specialty study guide — evaluation chapter':
                ('AWS ML Study Guide', 'https://aws.amazon.com/certification/certified-machine-learning-specialty/'),
            'SageMaker cost optimization guide':
                ('SageMaker Cost Optimization', 'https://docs.aws.amazon.com/sagemaker/latest/dg/cost-optimization-overview.html'),
            'AWS Well-Architected ML Lens':
                ('AWS Well-Architected ML Lens', 'https://docs.aws.amazon.com/wellarchitected/latest/machine-learning-lens/machine-learning-lens.html'),
            'Tutorials Dojo AWS ML Specialty — Timed Mode':
                ('Tutorials Dojo AWS ML', 'https://tutorialsdojo.com/courses/aws-certified-machine-learning-specialty-practice-exams/'),
            'Whizlabs final practice exam':
                ('Whizlabs AWS ML', 'https://www.whizlabs.com/aws-certified-machine-learning-specialty/'),
            'SageMaker Clarify docs':
                ('SageMaker Clarify', 'https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-fairness-and-explainability.html'),
            'AWS responsible AI whitepaper':
                ('AWS Responsible AI', 'https://aws.amazon.com/machine-learning/responsible-machine-learning/'),
            'Amazon Bedrock docs':
                ('Amazon Bedrock', 'https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html'),
            'AWS GenAI Learning Path':
                ('AWS GenAI Learning', 'https://aws.amazon.com/training/learn-about/generative-ai/'),
            'AWS AI Services overview':
                ('AWS AI Services', 'https://aws.amazon.com/ai/'),
            'SageMaker NLP examples':
                ('SageMaker NLP Examples', 'https://github.com/aws/amazon-sagemaker-examples'),
            'Amazon Forecast docs':
                ('Amazon Forecast', 'https://docs.aws.amazon.com/forecast/latest/dg/what-is-forecast.html'),
            'SageMaker DeepAR algorithm guide':
                ('SageMaker DeepAR', 'https://docs.aws.amazon.com/sagemaker/latest/dg/deepar.html'),
            'aws.training — schedule exam':
                ('AWS Exam Scheduling', 'https://www.aws.training/certification'),
            'Pearson VUE test centre locator':
                ('Pearson VUE', 'https://home.pearsonvue.com/aws'),
            'SageMaker Immersion Day (aws.amazon.com/getting-started)':
                ('SageMaker Immersion Day', 'https://catalog.us-east-1.prod.workshops.aws/workshops/63069e26-921c-4ce1-9cc7-debb66a991ef'),
            'SageMaker example notebooks on GitHub':
                ('SageMaker Example Notebooks', 'https://github.com/aws/amazon-sagemaker-examples'),
        },
        'task_links': [
            ('Review the exam guide PDF from AWS training site',
             'https://aws.amazon.com/certification/certified-machine-learning-specialty/'),
            ('Complete the SageMaker Immersion Day labs',
             'https://catalog.us-east-1.prod.workshops.aws/workshops/63069e26-921c-4ce1-9cc7-debb66a991ef'),
            ('Take a 65-question practice exam (Whizlabs or Tutorials Dojo)',
             'https://tutorialsdojo.com/courses/aws-certified-machine-learning-specialty-practice-exams/'),
            ('Book exam: $300 USD',
             'https://www.aws.training/certification'),
        ],
    },

    'powerbi-certified': {
        'resources': {
            'learn.microsoft.com/certifications/power-bi-data-analyst':
                ('Microsoft PL-300 Certification', 'https://learn.microsoft.com/en-us/certifications/power-bi-data-analyst/'),
            'Power BI Desktop download (powerbi.microsoft.com)':
                ('Power BI Desktop Download', 'https://powerbi.microsoft.com/en-us/desktop/'),
            'Power Query docs (learn.microsoft.com)':
                ('Power Query Docs', 'https://learn.microsoft.com/en-us/power-query/'),
            'Power Query M language reference':
                ('M Language Reference', 'https://learn.microsoft.com/en-us/powerquery-m/'),
            'Microsoft data modeling docs':
                ('Power BI Data Modeling', 'https://learn.microsoft.com/en-us/power-bi/transform-model/'),
            'SQLBI — star schema best practices':
                ('SQLBI Star Schema Guide', 'https://www.sqlbi.com/articles/creating-a-simple-date-table-in-dax/'),
            'DAX Guide (dax.guide)':
                ('DAX Guide', 'https://dax.guide/'),
            'SQLBI — DAX Patterns book (free online)':
                ('SQLBI DAX Patterns', 'https://www.daxpatterns.com/'),
            'SQLBI — Understanding CALCULATE':
                ('SQLBI: Understanding CALCULATE', 'https://www.sqlbi.com/articles/understanding-calculate-in-dax/'),
            'DAX Patterns: time intelligence (daxpatterns.com)':
                ('DAX Time Intelligence', 'https://www.daxpatterns.com/time-patterns/'),
            'Power BI RLS docs':
                ('Power BI RLS', 'https://learn.microsoft.com/en-us/power-bi/enterprise/service-admin-rls'),
            'SQLBI — role-playing dimensions guide':
                ('SQLBI Role-Playing Dimensions', 'https://www.sqlbi.com/articles/role-playing-dimensions-in-dax/'),
            'Power BI visualization docs':
                ('Power BI Visualizations', 'https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-types-for-reports-and-q-and-a'),
            'Microsoft PL-300 visualization module (Learn)':
                ('PL-300 Visualize Learning Path', 'https://learn.microsoft.com/en-us/training/paths/visualize-data-power-bi/'),
            'Power BI Service docs':
                ('Power BI Service', 'https://learn.microsoft.com/en-us/power-bi/fundamentals/service-get-started'),
            'Microsoft Learn — Deploy and maintain deliverables module':
                ('Deploy & Maintain Module', 'https://learn.microsoft.com/en-us/training/paths/deploy-manage-data-for-power-bi/'),
            'MeasureUp PL-300 practice exam':
                ('MeasureUp PL-300', 'https://www.measureup.com/pl-300-microsoft-power-bi-data-analyst.html'),
            'Whizlabs PL-300 practice tests':
                ('Whizlabs PL-300', 'https://www.whizlabs.com/microsoft-pl-300/'),
            'Power BI dataflows docs':
                ('Power BI Dataflows', 'https://learn.microsoft.com/en-us/power-bi/transform-model/dataflows/dataflows-introduction-self-service'),
            'Power BI storage modes comparison':
                ('Storage Modes', 'https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-storage-mode'),
            'Power BI deployment pipelines docs':
                ('Deployment Pipelines', 'https://learn.microsoft.com/en-us/power-bi/create-reports/deployment-pipelines-overview'),
            'Power BI Premium docs':
                ('Power BI Premium', 'https://learn.microsoft.com/en-us/power-bi/enterprise/service-premium-what-is'),
            'DAX Studio download (daxstudio.org)':
                ('DAX Studio', 'https://daxstudio.org/'),
            'SQLBI — optimize DAX models':
                ('SQLBI DAX Optimization', 'https://www.sqlbi.com/guides/dax/'),
            'Microsoft certification portal (learn.microsoft.com)':
                ('Microsoft Certification Portal', 'https://learn.microsoft.com/en-us/certifications/power-bi-data-analyst/'),
            'Pearson VUE — online proctoring options':
                ('Pearson VUE', 'https://home.pearsonvue.com/microsoft'),
            'Microsoft PL-300 skills measured document':
                ('PL-300 Skills Measured', 'https://learn.microsoft.com/en-us/certifications/resources/study-guides/pl-300'),
        },
        'task_links': [
            ('Install Power BI Desktop',
             'https://powerbi.microsoft.com/en-us/desktop/'),
            ('Complete the Microsoft Learn PL-300 learning path overview',
             'https://learn.microsoft.com/en-us/training/courses/pl-300t00'),
            ('Book exam: $165 USD',
             'https://learn.microsoft.com/en-us/certifications/power-bi-data-analyst/'),
        ],
    },
}

# ── CSS snippet to add after .res-pill rule ─────────────────────────────────
CSS_ADD = 'a.res-pill{text-decoration:none;cursor:pointer;}a.res-pill:hover{background:var(--surface3);border-color:var(--border2);color:var(--text);}.task-link{color:var(--blue-dark);font-size:11px;margin-left:6px;flex-shrink:0;opacity:0.7;line-height:1.5;}.task-link:hover{opacity:1;text-decoration:none;}'

# ── JS helper functions to add ──────────────────────────────────────────────
JS_HELPERS = (
    "function renderTask(t){if(typeof t==='string')return`<div class=\"task\"><div class=\"task-bullet\"></div><span>${t}</span></div>`;"
    "return`<div class=\"task\"><div class=\"task-bullet\"></div><span>${t.text}</span>${t.url?`<a class=\"task-link\" href=\"${t.url}\" target=\"_blank\" rel=\"noopener\">\u2197</a>`:''}</div>`;}"
    "\nfunction renderRes(r){if(typeof r==='string')return`<span class=\"res-pill\">\U0001f4ce ${r}</span>`;"
    "return r.url?`<a class=\"res-pill\" href=\"${r.url}\" target=\"_blank\" rel=\"noopener\">\U0001f4ce ${r.text}</a>`:`<span class=\"res-pill\">\U0001f4ce ${r.text}</span>`;}"
)

# strings to find/replace in renderSchedule
OLD_TASK_ROW = '<div class="task-list">${d.tasks.map(t=>`<div class="task"><div class="task-bullet"></div><span>${t}</span></div>`).join(\'\')}</div>'
NEW_TASK_ROW = '<div class="task-list">${d.tasks.map(renderTask).join(\'\')}</div>'

OLD_RES_ROW = '<div class="resources-row">${d.resources.map(r=>`<span class="res-pill">📎 ${r}</span>`).join(\'\')}</div>'
NEW_RES_ROW = '<div class="resources-row">${d.resources.map(renderRes).join(\'\')}</div>'

AFTER_BADGE_LABEL = "function badgeLabel(b){return{learn:'Learn',practice:'Practice',review:'Review',exam:'Exam'}[b];}"
AFTER_RES_PILL = '.res-pill{font-size:11px;padding:4px 11px;border-radius:99px;background:var(--surface2);border:.5px solid var(--border);color:var(--text2);}'


def extract_days_json(content):
    """Extract the days JSON array from the content, return (start, end, days_list)."""
    marker = 'const days='
    pos = content.index(marker) + len(marker)
    depth = 0
    end = pos
    for i, c in enumerate(content[pos:]):
        if c == '[':
            depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0:
                end = pos + i + 1
                break
    return pos, end, json.loads(content[pos:end])


def update_days(days_list, res_map, task_links):
    """Update resources and tasks in the days list with URLs."""
    for day in days_list:
        # Update resources
        new_resources = []
        for r in day.get('resources', []):
            if r in res_map:
                text, url = res_map[r]
                new_resources.append({'text': text, 'url': url})
            else:
                new_resources.append(r)
        day['resources'] = new_resources

        # Update tasks that match known patterns
        new_tasks = []
        for t in day.get('tasks', []):
            matched = False
            for (substr, url) in task_links:
                if substr in t:
                    new_tasks.append({'text': t, 'url': url})
                    matched = True
                    break
            if not matched:
                new_tasks.append(t)
        day['tasks'] = new_tasks
    return days_list


def process_course(course_id, data):
    path = os.path.join(BASE, course_id, 'index.html')
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    changed = False

    # 1. Add CSS after .res-pill rule
    if CSS_ADD not in content and AFTER_RES_PILL in content:
        content = content.replace(AFTER_RES_PILL, AFTER_RES_PILL + CSS_ADD)
        changed = True

    # 2. Add JS helper functions after badgeLabel
    if 'function renderTask' not in content and AFTER_BADGE_LABEL in content:
        content = content.replace(
            AFTER_BADGE_LABEL,
            AFTER_BADGE_LABEL + '\n' + JS_HELPERS
        )
        changed = True

    # 3. Update renderSchedule to use helpers
    if OLD_TASK_ROW in content:
        content = content.replace(OLD_TASK_ROW, NEW_TASK_ROW)
        changed = True
    if OLD_RES_ROW in content:
        content = content.replace(OLD_RES_ROW, NEW_RES_ROW)
        changed = True

    # 4. Update days data
    try:
        pos, end, days_list = extract_days_json(content)
        updated = update_days(days_list, data['resources'], data['task_links'])
        new_json = json.dumps(updated, ensure_ascii=False, separators=(',', ':'))
        content = content[:pos] + new_json + content[end:]
        changed = True
    except Exception as e:
        print(f'  ⚠ days JSON update failed for {course_id}: {e}')

    if changed:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'✓ {course_id}')
    else:
        print(f'— {course_id} (no changes)')


for course_id, data in COURSE_DATA.items():
    process_course(course_id, data)

print('\nDone.')
