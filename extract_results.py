import json, os, sys, importlib
from typing import Optional


import pandas as pd
from collections import defaultdict
from logger import mylog
from benchmarking import dataset_key_to_base_fname, get_bench_path

logger = mylog.get_logger()

PRINT_LATEX = False

def calc(bench_id: str, paths: dict[str, list[str]], method_names_to_prefixes: dict[str, str], expected_prediction: Optional[bool] = False, dataset_to_method_stats= None, is_clf=False):
    bench_path = get_bench_path(bench_id)
    if dataset_to_method_stats is None:
        dataset_to_method_stats = defaultdict(lambda: defaultdict(lambda: {'wrong': 0, 'total': 0}))
    for dataset_key, dataset_paths in paths.items():
        # logger.info(f"Calculating results for {dataset_key}..")
        for file_key in dataset_paths:
            file_path = os.path.join(bench_path, dataset_key_to_base_fname[file_key]+".json")

            with open(file_path, 'r') as f:
                data = json.load(f)
            for sample_id, prediction in data.items():
                for method_name, method_prefix in method_names_to_prefixes.items():
                    for possible_prediction_key, possible_prediction_value in prediction.items():
                        if possible_prediction_key.startswith(method_prefix):
                            if dataset_key == 'STS':
                                score = prediction['score']
                                if score < 0 or score >= 3:
                                    # print(f"ignored score {score} for {dataset_key}")
                                    continue
                            if dataset_key == 'SICK':
                                score = prediction['score']
                                if score < 1 or score >= 3:
                                    # print(f"ignored score {score} for {dataset_key}")
                                    continue
                            # print(expected_prediction)
                            if is_clf:
                                if dataset_key == 'STS-H':
                                    if 'label' not in prediction:
                                        # unlabelled, not part of the dataset
                                        continue
                                    expected_prediction = prediction['label']
                                else:
                                    expected_prediction = (prediction['label'] == 1)
                            dataset_to_method_stats[dataset_key][method_name]['total'] += 1
                            if possible_prediction_value != expected_prediction:
                                dataset_to_method_stats[dataset_key][method_name]['wrong'] += 1
                            elif possible_prediction_value == expected_prediction:
                                pass
                            else:
                                logger.error(
                                    f"Unexpected prediction value {possible_prediction_value} for method {method_name}!")
                                raise Exception(
                                    f"Unexpected prediction value {possible_prediction_value} for method {method_name}!")


    data = {}


    # Populate the data dictionary
    for dataset_key, method_stat_dict in dataset_to_method_stats.items():
        for method_name, stats in method_stat_dict.items():
            wrong = stats["wrong"]
            total = stats["total"]
            error_rate = (wrong / total) * 100



            if dataset_key not in data:
                data[dataset_key] = {}
            if method_name not in data[dataset_key]:
                data[dataset_key][method_name] = {}

            data[dataset_key][method_name] = f"{error_rate:.1f}%"

    # df = pd.DataFrame(data)
    # logger.info("\n" + df.to_string())


    return data




# Load configuration file
def load_config(config_path):
    with open(config_path, "r") as config_file:
        return json.load(config_file)


def rate_calc(bench_id: str, paths: dict[str, list[str]]):
    def read_r(p):
        try:
            with open(p, 'r') as f:
                return json.load(f)
        except Exception as e:
            return {}

    bench_path = get_bench_path(bench_id)

    info_by_dataset_by_method = {}

    for dataset_key, dataset_paths in paths.items():
        # logger.info(f"Calculating results for {dataset_key}..")
        for file_key in dataset_paths:
            succ_file_path = os.path.join(bench_path, "succ_"+dataset_key_to_base_fname[file_key] + ".json")
            fail_file_path = os.path.join(bench_path, "faults_" + dataset_key_to_base_fname[file_key] + ".json")
            file_path = os.path.join(bench_path, dataset_key_to_base_fname[file_key] + ".json")

            records = read_r(file_path)
            successes = read_r(succ_file_path)
            fails = read_r(fail_file_path)

            info_by_method = {}

            def note_method(method_name: str, succ: bool):
                if method_name not in info_by_method:
                    info_by_method[method_name] = {}
                    info_by_method[method_name]["succ"] = 0
                    info_by_method[method_name]["fail"] = 0
                    info_by_method[method_name]["total"] = 0
                key = "succ" if succ else "fail"

                info_by_method[method_name][key] += 1

            def note_method_total(method_name: str):
                if method_name not in info_by_method:
                    print(f"This should not happen because note_method shoulr run at least one before this function.")
                    exit(-1)
                info_by_method[method_name]["total"] += 1


            for sample_id, prediction in records.items():
                methods_to_note_in_total = set()
                if sample_id in successes:
                    for method_key in successes[sample_id]:
                        note_method(method_key, True)
                        methods_to_note_in_total.add(method_key)
                if sample_id in fails:
                    for method_key in fails[sample_id]:
                        note_method(method_key, False)
                        methods_to_note_in_total.add(method_key)
                # for each sample id that was noted as either successfully or unsuccessfully predicted,
                # add it to the total.
                # Note:
                # because not all predictions may have been noted (benches ran with an older version of the benchmark), we need to note the total of what was *actually* tracked as success or fail.

                for method_key in methods_to_note_in_total:
                    note_method_total(method_key)
#           all samples from the dataset 'file_key' have been extracted.
            info_by_dataset_by_method[file_key] = info_by_method

    fail_avgs_by_method = {}
    succ_avgs_by_method = {}



    for dataset_key, ddict in info_by_dataset_by_method.items():
        for method_name, results_dict in ddict.items():
            if method_name not in fail_avgs_by_method:
                fail_avgs_by_method[method_name] = []
            if method_name not in succ_avgs_by_method:
                succ_avgs_by_method[method_name] = []

            fail_avg = results_dict["fail"] / results_dict["total"]
            fail_avgs_by_method[method_name].append(fail_avg)

            succ_avg = results_dict["succ"] / results_dict["total"]
            succ_avgs_by_method[method_name].append(succ_avg)


    stuff_by_method = {}
    for method_name, avgs in fail_avgs_by_method.items():
        s=0
        for i in avgs:
           s+=i
        a = s/len(avgs)
        if method_name not in stuff_by_method:
            stuff_by_method[method_name] = f"\n{method_name}:"
        stuff_by_method[method_name]+=f"\tfail: {a*100:.2f}%"

    for method_name, avgs in succ_avgs_by_method.items():
        s=0
        for i in avgs:
           s+=i
        a = s/len(avgs)
        if method_name not in stuff_by_method:
            stuff_by_method[method_name] = f"\n{method_name}:"
        stuff_by_method[method_name]+=f"\tsucc: {a*100:.2f}%"

    for _, s in stuff_by_method.items():
        print(s)

    stats_path = os.path.join(bench_path, "rates.json")
    with open(stats_path, 'w') as f:
        json.dump(info_by_dataset_by_method, f, indent=3, ensure_ascii=False)



if __name__ == '__main__':
    clf_dataset_group_keys = {
        "PAWSX": [
            "pawsx_test"
        ],
        "STS-H": ["stsbenchmark"],
        "MRPC": ["ms_mrpc"]
    }


    min_dataset_group_keys = {
        "SNLI": [
            "stanfordnlp_snli_pre_hyp",
            "stanfordnlp_snli_hyp_pre"
        ],
    "ANLI": [
        "fb_anli_pre_hyp",
        "fb_anli_hyp_pre"
    ],
        "XNLI": [
            "fb_xnli_pre_hyp",
            "fb_xnli_hyp_pre"
        ],
    "STS": ["stsbenchmark"],


    "SICK": ["sickr_sts"]
    }
    max_dataset_group_keys = {
        "TRUE": ["simple_amr"],
        "SIMP": [
            "onestop_all"
        ]

    }





    if len(sys.argv) == 1:
        config_path = "paper_config.json"
    elif len(sys.argv) == 2:
        config_path = sys.argv[1]
    else:
        print("Please specify a config path!")
        exit(1)

    config = load_config(config_path)
    bench_id = config["bench_id"]
    if "prefixes" in config:
        prefixes = config["prefixes"]
    else:
        m = config["methods"]
        prefixes = {}
        for method in m:
            n = method["name"]
            prefixes[n] = n

    min = calc(bench_id, min_dataset_group_keys, method_names_to_prefixes=prefixes, expected_prediction=False)
    max = calc(bench_id, max_dataset_group_keys, method_names_to_prefixes=prefixes, expected_prediction=True)
    clf = calc(bench_id, clf_dataset_group_keys, method_names_to_prefixes=prefixes, expected_prediction=None, is_clf=True)

    results = {
        'Classify!': clf,
        'Minimize!': min,
        'Maximize!': max
    }
    kind_totals_by_method = {}
    for kind, dict in results.items():
        kind_totals_by_method[kind] = {}
        for dataset, methods_dict in dict.items():
            for method_name, rate in methods_dict.items():
                if method_name not in kind_totals_by_method[kind]:
                    kind_totals_by_method[kind][method_name] = []
                rate = float(rate.replace("%", ""))
                kind_totals_by_method[kind][method_name].append(rate)


    avg_by_method_by_kind = {}



    # calculate average of each method by kind (kind is min, max, clf)
    # and grand total for each method
    grand_totals_by_method = {}
    for kind, totals_dict in kind_totals_by_method.items():
        for method_name, totals in totals_dict.items():
            sum=0
            for i in totals:
                sum += i
            avg = sum/len(totals)
            if method_name not in grand_totals_by_method:
                grand_totals_by_method[method_name] = []
            grand_totals_by_method[method_name].append(avg)

            if method_name not in avg_by_method_by_kind:
                avg_by_method_by_kind[method_name] = {}
            avg_by_method_by_kind[method_name][kind] = f"{avg:.1f}%"

    b1 = {}
    for method_name, totals_dict in avg_by_method_by_kind.items():
        b1[method_name] = 0
        for kind, avg in totals_dict.items():
            b1[method_name] += float(avg.replace("%", ""))
        b1[method_name] = b1[method_name] / 3

    for method_name, a in b1.items():
        avg_by_method_by_kind[method_name]["Overall Average"] = f"{a:.1f}%"



    results["Averages"] = avg_by_method_by_kind

    final_keys_ordering = [
        "Classify!",
        "Minimize!",
        "Maximize!",
        "Overall Average"
    ]

    if PRINT_LATEX:
        for method_name in avg_by_method_by_kind.keys():
            s = method_name
            s+="\n"
            for method in clf_dataset_group_keys.keys():
                # print(method)
                rate = results["Classify!"][method][method_name]
                rate = rate.replace("%", "")
                s+=f"& {rate} "
            for method in min_dataset_group_keys.keys():
                # print(method)
                rate = results["Minimize!"][method][method_name]
                rate = rate.replace("%", "")
                s += f"& {rate} "
            for method in max_dataset_group_keys.keys():
                # print(method)
                rate = results["Maximize!"][method][method_name]
                rate = rate.replace("%", "")
                s += f"& {rate} "
            for method in final_keys_ordering:
                # print(method)
                rate = avg_by_method_by_kind[method_name][method]
                rate = rate.replace("%", "")
                s += f"& {rate} "


            print(s+"\n")




    bench_path = get_bench_path(bench_id)
    result_path = os.path.join(bench_path, "results.json")
    with open(result_path, 'w') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)


    def all_keys(current, new):
        for k, v in new.items():
            current[k] = v
        return current


    alls = {}
    alls = all_keys(alls, min_dataset_group_keys)
    alls = all_keys(alls, max_dataset_group_keys)
    alls = all_keys(alls, clf_dataset_group_keys)
    rate_calc(bench_id, alls)
    print(f"Results for {bench_id} written to {result_path}")
